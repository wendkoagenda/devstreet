"""
Villes par pays pour les formulaires (pays, ville, téléphone).

Source : l'API publique CountriesNow (sans clé), interrogée par le serveur uniquement. Le navigateur ne parle
qu'à DevStreet. La liste complète (environ 1 Mo) est mise en cache 30 jours ; un échec est mis en cache
quelques minutes pour ne pas solliciter un service en panne à chaque requête.

Les données de l'API ont des manques sur nos marchés principaux (Ouagadougou absente pour le Burkina Faso,
par exemple) : une liste de grandes villes, maintenue ici, est fusionnée en tête des résultats.
Le formulaire accepte toujours une ville absente de la liste (saisie libre).
"""
import logging
import re
from typing import Dict, List, Optional

import httpx
from django.core.cache import cache

logger = logging.getLogger(__name__)

SOURCE_URL = 'https://countriesnow.space/api/v0.1/countries'
CACHE_KEY = 'geo:cities-by-country:v1'
CACHE_TTL_SECONDS = 30 * 24 * 3600
FAILURE_CACHE_KEY = 'geo:cities-by-country:failure'
FAILURE_TTL_SECONDS = 5 * 60
REQUEST_TIMEOUT_SECONDS = 15

ISO2_RE = re.compile(r'^[A-Z]{2}$')

# Grandes villes des pays mis en avant dans les formulaires, affichées en premier.
MAJOR_CITIES: Dict[str, List[str]] = {
    'BJ': ['Cotonou', 'Porto-Novo', 'Parakou', 'Abomey-Calavi', 'Djougou', 'Bohicon', 'Natitingou', 'Lokossa', 'Ouidah'],
    'BF': ['Ouagadougou', 'Bobo-Dioulasso', 'Koudougou', 'Ouahigouya', 'Banfora', 'Dédougou', 'Kaya', 'Tenkodogo',
           'Fada N\'Gourma', 'Dori', 'Gaoua', 'Ziniaré'],
    'CM': ['Douala', 'Yaoundé', 'Garoua', 'Bamenda', 'Bafoussam', 'Maroua', 'Ngaoundéré', 'Bertoua', 'Kribi', 'Limbé'],
    'CI': ['Abidjan', 'Yamoussoukro', 'Bouaké', 'Daloa', 'San-Pédro', 'Korhogo', 'Man', 'Gagnoa', 'Divo', 'Grand-Bassam'],
    'GA': ['Libreville', 'Port-Gentil', 'Franceville', 'Oyem', 'Moanda', 'Lambaréné'],
    'GH': ['Accra', 'Kumasi', 'Tamale', 'Takoradi', 'Cape Coast', 'Tema', 'Koforidua', 'Ho'],
    'GN': ['Conakry', 'Nzérékoré', 'Kankan', 'Kindia', 'Labé', 'Boké', 'Mamou', 'Siguiri'],
    'ML': ['Bamako', 'Sikasso', 'Mopti', 'Koutiala', 'Ségou', 'Kayes', 'Gao', 'Tombouctou', 'Kati'],
    'MA': ['Casablanca', 'Rabat', 'Marrakech', 'Fès', 'Tanger', 'Agadir', 'Meknès', 'Oujda', 'Kénitra', 'Tétouan'],
    'NE': ['Niamey', 'Zinder', 'Maradi', 'Agadez', 'Tahoua', 'Dosso', 'Diffa', 'Tillabéri'],
    'NG': ['Lagos', 'Abuja', 'Kano', 'Ibadan', 'Port Harcourt', 'Benin City', 'Kaduna', 'Enugu', 'Abeokuta', 'Jos'],
    'CD': ['Kinshasa', 'Lubumbashi', 'Mbuji-Mayi', 'Kisangani', 'Goma', 'Bukavu', 'Kananga', 'Matadi', 'Kolwezi'],
    'SN': ['Dakar', 'Thiès', 'Saint-Louis', 'Touba', 'Kaolack', 'Ziguinchor', 'Mbour', 'Rufisque', 'Diourbel', 'Louga'],
    'TG': ['Lomé', 'Sokodé', 'Kara', 'Kpalimé', 'Atakpamé', 'Dapaong', 'Tsévié', 'Aného'],
    'TN': ['Tunis', 'Sfax', 'Sousse', 'Kairouan', 'Bizerte', 'Gabès', 'Ariana', 'Monastir', 'Nabeul'],
    'FR': ['Paris', 'Marseille', 'Lyon', 'Toulouse', 'Nice', 'Nantes', 'Strasbourg', 'Montpellier', 'Bordeaux',
           'Lille', 'Rennes', 'Reims', 'Grenoble'],
    'BE': ['Bruxelles', 'Anvers', 'Gand', 'Charleroi', 'Liège', 'Bruges', 'Namur', 'Louvain', 'Mons'],
    'CA': ['Montréal', 'Toronto', 'Vancouver', 'Ottawa', 'Québec', 'Calgary', 'Edmonton', 'Winnipeg', 'Gatineau',
           'Sherbrooke'],
}


class CitiesUnavailable(Exception):
    """Le service public des villes ne répond pas ou renvoie une réponse inattendue."""


def _fetch_all() -> Dict[str, List[str]]:
    """
    Télécharge la liste complète {ISO2: [villes]}.

    Raises:
        CitiesUnavailable: service injoignable, en erreur ou réponse inattendue
    """
    try:
        response = httpx.get(SOURCE_URL, timeout=REQUEST_TIMEOUT_SECONDS)
        response.raise_for_status()
        payload = response.json()
    except (httpx.HTTPError, ValueError) as error:
        logger.warning("Liste des villes indisponible (%s)", SOURCE_URL, exc_info=True)
        raise CitiesUnavailable(str(error)) from error
    if payload.get('error') or not isinstance(payload.get('data'), list):
        raise CitiesUnavailable("Réponse inattendue du service des villes")
    result: Dict[str, List[str]] = {}
    for row in payload['data']:
        iso2 = str(row.get('iso2') or '').upper()
        cities = row.get('cities')
        if ISO2_RE.match(iso2) and isinstance(cities, list):
            result[iso2] = [str(city).strip() for city in cities if str(city).strip()]
    return result


def _all_cities() -> Optional[Dict[str, List[str]]]:
    """
    Liste complète depuis le cache, téléchargée au besoin.

    Retourne None quand le service est en panne : la panne est mémorisée quelques minutes pour ne pas
    le solliciter à chaque requête, et l'appelant se replie sur les grandes villes ou la saisie libre.
    """
    data = cache.get(CACHE_KEY)
    if data is not None:
        return data
    if cache.get(FAILURE_CACHE_KEY):
        return None
    try:
        data = _fetch_all()
    except CitiesUnavailable as error:
        logger.warning("Villes indisponibles, nouvel essai dans %s s : %s", FAILURE_TTL_SECONDS, error)
        cache.set(FAILURE_CACHE_KEY, True, FAILURE_TTL_SECONDS)
        return None
    cache.set(CACHE_KEY, data, CACHE_TTL_SECONDS)
    return data


def cities_for(country_code: str) -> dict:
    """
    Villes d'un pays : grandes villes d'abord, puis la liste de l'API (sans doublon, ordre alphabétique).

    Returns:
        {"country": "BF", "cities": [...], "available": bool}. `available` vaut False quand le service est
        indisponible et qu'aucune grande ville n'est connue pour ce pays : le formulaire passe en saisie libre.
    """
    code = (country_code or '').upper()
    if not ISO2_RE.match(code):
        return {'country': code, 'cities': [], 'available': False}

    major = MAJOR_CITIES.get(code, [])
    remote = (_all_cities() or {}).get(code, [])
    seen = set()
    merged: List[str] = []
    for city in major + sorted(remote, key=str.casefold):
        key = city.casefold()
        if key not in seen:
            seen.add(key)
            merged.append(city)
    return {'country': code, 'cities': merged, 'available': bool(merged)}
