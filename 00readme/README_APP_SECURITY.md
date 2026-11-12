# Remote Devops - Securite applicative deterministe

## Objectif

Ajouter a Remote Devops une section **Securite applicative** pour analyser les depots et les artefacts des applications web deployees avec des regles deterministes, lisibles et testables.

Le but n'est pas de remplacer GitHub Advanced Security, Snyk, Semgrep Cloud ou un programme AppSec complet. Le but est de proposer un cockpit simple et actionnable pour une petite equipe :

- voir les risques ;
- comprendre quelle regle a ete violee ;
- prioriser les corrections ;
- auditer les exceptions ;
- verifier qu'une correction tient dans le temps.

Principe central : **pas de boite noire**. Un finding doit etre explicable par une regle precise.

---

## Inspiration `herald-engine`

`herald-engine` se presente comme un moteur d'analyse de code deterministe, sans IA et sans stockage. Il applique des regles explicites au code et retourne des problemes precis ainsi qu'un score.

Le depot annonce notamment :

- un moteur `herald-engine` avec parsers `tree-sitter`, langage de regles `.herald`, analyseurs built-in et scoring ;
- un CLI `herald-cli` pour analyser des fichiers localement ;
- une sortie JSON ;
- un code de sortie non nul en cas d'erreurs, utile en CI ;
- des regles lisibles et testables.

Le DSL `.herald` est structure autour de trois familles :

- `match` / `when` : reconnaissance de formes dangereuses dans l'AST, avec conditions pour limiter les faux positifs ;
- `measure` : metriques de taille ou complexite, par exemple lignes de fonction, complexite, nesting ;
- `use` : analyseurs built-in pour les cas plus complexes.

Point juridique a verifier avant toute integration directe : le depot est sous licence **AGPL-3.0-only**. Si Remote Devops expose une version modifiee du moteur comme service reseau, il faudra analyser les obligations de publication du code source des modifications.

Sources :

- https://github.com/async-herald/herald-engine
- https://github.com/async-herald/herald-engine/blob/main/crates/herald-engine/src/dsl/README.md

---

## Positionnement produit

### Nom de section propose

Dans la sidebar :

- **Securite**

Sous-sections possibles :

- **Vue d'ensemble**
- **Findings**
- **Regles**
- **Rapports**
- **Exceptions**
- **Historique**

### Ce que l'utilisateur doit comprendre

Pour chaque application/depot :

- Est-ce que l'application respecte les regles de securite minimales ?
- Quels risques sont nouveaux ?
- Quels risques existaient deja avant la PR ou le deploiement ?
- Est-ce bloquant pour deployer ?
- Quelle action concrete faut-il faire ?
- Qui a ignore un finding, pourquoi, et jusqu'a quand ?

---

## Modele mental

Remote Devops connait deja :

- des organisations ;
- des projets GCP ;
- des depots GitHub ;
- des VM ;
- des environnements GitHub ;
- des audits d'actions.

La section securite ajoute une couche :

```text
Organisation
  -> Depot GitHub
    -> Application
      -> Environnement
        -> Scan securite
        -> Findings
        -> Regles
        -> Exceptions
```

Une application peut etre rattachee a :

- un depot GitHub ;
- un projet GCP ;
- une ou plusieurs VM ;
- un environnement (`dev`, `staging`, `prod`) ;
- une URL publique ou interne ;
- une stack technique declaree (`Django`, `React`, `Vite`, `Node`, etc.).

---

## Types de scans

### 1. Scan depot

Analyse le code du depot GitHub lie a une application.

Declencheurs possibles :

- manuel depuis Remote Devops ;
- a chaque synchronisation de depot ;
- planifie chaque nuit ;
- apres un deploiement.

Resultat attendu :

- score global ;
- nombre d'erreurs, warnings, infos ;
- liste des findings ;
- comparaison avec le dernier scan.

### 2. Scan PR

Analyse uniquement les fichiers modifies dans une Pull Request.

Objectif :

- eviter de bloquer une PR sur toute la dette historique ;
- bloquer seulement les nouvelles regressions ;
- afficher les problemes introduits par la PR.

### 3. Scan release/deploiement

Analyse un commit, tag ou SHA associe a un deploiement.

Objectif :

- garder une trace de l'etat securite au moment du deploiement ;
- savoir si une version en production contient des findings critiques ;
- relier une regression a un deploiement precis.

### 4. Scan configuration runtime

Analyse les fichiers et variables de configuration non secretes :

- headers HTTP attendus ;
- configuration CORS ;
- cookies ;
- mode debug ;
- variables publiques frontend ;
- configuration proxy ;
- routes exposees.

Attention : les valeurs secretes ne doivent jamais etre stockees ni affichees.

---

## Regles de securite prioritaires

### Authentification et session

Regles proposees :

- JWT stocke dans `localStorage` ou `sessionStorage`.
- Cookie d'auth sans `HttpOnly`.
- Cookie d'auth sans `Secure` en environnement HTTPS.
- Cookie sensible avec `SameSite=None` sans justification.
- Endpoint de logout absent ou non protege.
- Refresh token expose au frontend.
- Token ou secret present dans une reponse JSON de login.
- Verification CSRF absente sur mutations authentifiees par cookie.

Interet pour Remote Devops :

- le projet a deja une orientation same-origin + cookies HttpOnly ;
- ces regles evitent de casser ce modele dans les evolutions futures.

### Secrets et credentials

Regles proposees :

- secret hardcode dans le code ;
- cle API detectee par nom de variable + entropie ;
- fichier `.env` commite ;
- fichier de compte de service GCP commite ;
- cle privee SSH presente dans le depot ;
- token GitHub ou Google expose dans une variable frontend `VITE_*` ;
- secret affiche dans un log ;
- secret transmis a l'UI alors qu'il devrait rester serveur.

Severite recommandee :

- `error` si secret probable ;
- `warning` si placeholder dangereux (`changeme`, `secret`, `token_here`) ;
- `info` si variable sensible correctement referencee via env.

### Injection

Regles proposees :

- execution shell avec entree dynamique ;
- SQL brut concatene avec entree utilisateur ;
- requete ORM unsafe quand applicable ;
- template string non echappee dans HTML ;
- appel HTTP construit avec URL non validee ;
- path filesystem construit avec entree utilisateur sans normalisation ;
- deserialisation dangereuse.

Exemples de familles :

- command injection ;
- SQL injection ;
- path traversal ;
- SSRF ;
- XSS ;
- unsafe deserialization.

### API et permissions

Regles proposees :

- endpoint DRF sans permission explicite ;
- `AllowAny` sur endpoint sensible ;
- action destructive sans confirmation ;
- action destructive sans audit ;
- endpoint admin expose sans restriction ;
- absence de rate limiting sur login, refresh ou action sensible ;
- mutation sans verification d'organisation/tenant ;
- acces objet sans filtrage par organisation.

Pour Remote Devops, c'est une famille importante : l'application manipule des actions cloud sensibles.

### Frontend

Regles proposees :

- appel API avec URL absolue au lieu d'un chemin same-origin ;
- fetch sans `credentials: "include"` pour une API cookie-based ;
- mutation sans CSRF ;
- affichage d'un secret en clair ;
- stockage local de token ;
- bouton d'action dangereuse sans confirmation ;
- formulaire sensible sans feedback d'erreur clair ;
- lien externe sans `rel="noopener noreferrer"` ;
- `dangerouslySetInnerHTML` sans sanitation explicite.

### Configuration de production

Regles proposees :

- `DEBUG=True` en production ;
- `ALLOWED_HOSTS=*` ;
- `CORS_ALLOW_ALL_ORIGINS=True` ;
- `CSRF_TRUSTED_ORIGINS` vide ou trop large ;
- cookies non secure en HTTPS ;
- source maps publiques en production sans decision explicite ;
- headers de securite absents ;
- endpoint Swagger public en production sans protection.

### Supply chain

Regles proposees :

- dependance avec version flottante ;
- package lock absent ;
- package abandonne ou non maintenu ;
- script npm suspect ;
- dependency confusion possible ;
- image Docker base non pinnee ;
- Dockerfile executant en root sans justification.

Cette partie peut commencer simple et s'enrichir plus tard.

---

## Scoring securite

### Score global

Score propose : `0` a `100`.

Calcul simple :

- depart a `100` ;
- `error` critique : -20 ;
- `error` standard : -10 ;
- `warning` : -3 ;
- `info` : pas de malus ;
- bonus possible si toutes les regles obligatoires passent.

Le score doit rester comprehensible. L'utilisateur doit voir pourquoi le score baisse.

### Etats

| Score | Etat | Sens |
| --- | --- | --- |
| 90-100 | Sain | Rien de bloquant |
| 75-89 | A surveiller | Dette faible ou moyenne |
| 50-74 | Risque eleve | Corrections recommandees avant prod |
| 0-49 | Bloquant | Ne pas deployer sans decision explicite |

### Gates de deploiement

Proposition :

- `prod` : aucun `security/error` nouveau ;
- `staging` : warnings autorises, errors visibles ;
- `dev` : jamais bloquant, mais suivi historique.

Le blocage doit etre configurable par organisation et par depot.

---

## Experience UI

### Page liste

Colonnes :

- Application ;
- Depot ;
- Environnement ;
- Dernier scan ;
- Score ;
- Erreurs ;
- Warnings ;
- Evolution ;
- Gate ;
- Action.

Filtres :

- organisation ;
- depot ;
- environnement ;
- severite ;
- type de regle ;
- nouveau depuis le dernier scan ;
- bloquant deploiement.

### Page detail application

Onglets :

- Vue d'ensemble ;
- Findings ;
- Regles ;
- Historique ;
- Deploiements ;
- Exceptions.

Bloc principal :

- score securite ;
- top 3 risques ;
- nouvelles regressions ;
- dette connue ;
- dernier commit analyse ;
- lien vers depot / PR / environnement.

### Finding detail

Afficher :

- ID regle ;
- titre ;
- severite ;
- fichier et ligne ;
- extrait court ;
- explication ;
- recommandation ;
- premiere detection ;
- derniere detection ;
- statut.

Statuts :

- nouveau ;
- confirme ;
- ignore avec justification ;
- corrige ;
- regresse ;
- faux positif.

### Exceptions

Une exception doit toujours avoir :

- une justification ;
- un auteur ;
- une date d'expiration ;
- une portee limitee : fichier, regle, depot ou environnement ;
- une trace d'audit.

Pas d'exception permanente par defaut.

---

## Regles et packs

### Packs de regles proposes

- `remote-devops-baseline`
- `django-api`
- `react-spa`
- `same-origin-cookies`
- `gcp-safe-ops`
- `github-actions-secrets`
- `docker-production`

### Gestion des regles

Chaque regle doit avoir :

- ID stable ;
- titre ;
- description ;
- severite ;
- categorie ;
- langage ou source concernee ;
- exemples fail/pass ;
- seuil configurable si applicable ;
- lien vers documentation interne.

---

## Rapports

### Rapport par application

Contenu :

- score securite ;
- findings critiques ;
- nouvelles regressions ;
- exceptions actives ;
- recommandations prioritaires.

Format :

- affichage UI ;
- export Markdown ;
- export PDF plus tard ;
- commentaire automatique sur PR plus tard.

### Rapport de release

Genere avant ou apres deploiement :

- commit / tag ;
- environnement ;
- score securite ;
- nouveaux risques ;
- decision : deployable / a verifier / bloque.

---

## Workflow recommande

### 1. Enregistrer une application

Champs :

- nom ;
- organisation ;
- depot GitHub ;
- projet GCP ;
- environnement ;
- URL ;
- type : frontend, backend, full-stack ;
- stack ;
- VM associees.

### 2. Lancer un premier scan

Remote Devops affiche :

- baseline securite ;
- dette existante ;
- premiers risques prioritaires.

### 3. Activer le suivi

Declencheurs :

- scan manuel ;
- scan PR ;
- scan nightly ;
- scan apres deploiement ;
- scan apres action infra sensible.

### 4. Definir les gates

Exemples :

- bloquer prod si nouveau `security/error` ;
- autoriser les warnings si exception justifiee ;
- bloquer une release si un secret probable est detecte.

### 5. Suivre les regressions

Remote Devops doit distinguer :

- dette historique ;
- nouveau probleme ;
- probleme corrige ;
- probleme revenu ;
- exception temporaire.

---

## Audit et securite interne

Toute action doit etre auditee :

- lancement de scan ;
- modification de regle ;
- changement de seuil ;
- creation d'exception ;
- suppression d'exception ;
- modification d'un gate ;
- decision de deploiement malgre risque.

Les rapports ne doivent jamais stocker :

- secrets ;
- tokens ;
- cles privees ;
- valeurs completes de variables sensibles ;
- payloads utilisateurs.

Les extraits de code doivent etre courts et masques si une valeur ressemble a un secret.

---

## Priorisation MVP

### MVP 1 - Scan depot manuel

Fonctionnalites :

- enregistrer une application liee a un depot ;
- lancer un scan manuel ;
- importer sortie JSON d'un moteur deterministe ;
- afficher score et findings ;
- filtrer par severite ;
- statut `nouveau`, `ignore`, `corrige` ;
- audit des scans et exceptions.

Regles prioritaires :

- secrets hardcodes ;
- tokens frontend ;
- JWT localStorage ;
- `AllowAny` sensible ;
- debug/config prod dangereuse ;
- action destructive sans audit/confirmation ;
- CORS/CSRF/cookies dangereux.

### MVP 2 - Scan PR et release

Fonctionnalites :

- comparer une PR a la baseline ;
- afficher uniquement les nouveaux findings ;
- stocker le score par release ;
- generer un rapport de release.

### MVP 3 - Gates de deploiement

Fonctionnalites :

- seuils par environnement ;
- decision `deployable`, `a verifier`, `bloque` ;
- commentaire ou rapport sur PR ;
- historique par release.

### MVP 4 - Packs de regles custom

Fonctionnalites :

- editeur/registre de regles ;
- tests fail/pass ;
- versioning ;
- exceptions expirees ;
- packs par stack.

---

## Idees d'ecrans

### Ecran `Securite`

Resume transverse :

- applications suivies ;
- scans recents ;
- score moyen securite ;
- regressions ouvertes ;
- gates bloques.

### Ecran `Findings`

Vue orientee investigation :

- score ;
- categories ;
- liste findings ;
- details ;
- exceptions.

### Ecran `Release Check`

Vue decisionnelle :

- commit ;
- environnement ;
- securite ;
- nouveaux problemes ;
- decision ;
- bouton `Valider le deploiement` si autorise.

---

## Definition de termine

Une premiere version est terminee si :

- une application peut etre rattachee a un depot et un environnement ;
- un scan securite manuel produit un score et des findings ;
- les findings sont explicables et filtrables ;
- une exception temporaire peut etre creee avec justification ;
- aucun secret n'est stocke ou affiche ;
- chaque action sensible est auditee.

---

## Questions a trancher

1. Le moteur deterministe sera-t-il integre directement, appele via CLI, ou execute dans une GitHub Action ?
2. Les scans doivent-ils analyser le depot complet ou seulement les changements depuis le dernier scan ?
3. Les gates doivent-ils bloquer techniquement le deploiement ou seulement afficher une decision ?
4. Quelle est la premiere stack ciblee : Django/React uniquement, ou multi-stack des le depart ?
5. Les rapports doivent-ils rester internes a Remote Devops ou etre publies dans GitHub ?
6. Faut-il stocker des extraits de code, ou uniquement fichier/ligne/message pour limiter le risque ?

