# Plan : profils dev et entreprise

> PRD source : [PRD.md](PRD.md). Ce plan est distinct de `docs/PLAN.md` (module Communauté). Les trois tranches validées sont : A (phases 1 à 3), B (phases 4 et 5), C (phases 6 à 10). Chaque phase passe par le workflow `git-cli` (branche et PR dédiées).

## Avancement (14 novembre 2026)

Les dix phases sont **codées dans l'arbre de travail**, sans commit ni push. Vérifié : `manage.py check`, absence de migration en attente de génération, scanner de sécurité (100/100), lint frontend (0 erreur). **Non vérifié** (à lancer sur demande) : tests backend (nouveaux : `test_username_rules`, `test_profils_dev_entreprise`), tests Vitest, build frontend, parcours dans le navigateur, application des migrations sur une vraie base. Écarts assumés par rapport au plan :

- Liste de noms réservés réduite (sans `admin`) car des comptes de démonstration l'utilisent.
- Phase 3 : `/marketplace/profiles/:id` est redirigée en phase 6 (identifiant de profil, pas de membre) ; la page Hub `/hub/profiles/:userId` n'est plus routée (son contenu est couvert par l'onglet Projets).
- Phase 8 : la création d'entreprise exige toujours un profil dev existant (inchangé) ; elle crée désormais le profil entreprise propriétaire.
- Phase 10 : un membre invité n'a qu'un profil entreprise ; l'espace recruteur fonctionne, mais le tableau de bord candidat lui demande de créer un profil dev.
- Seul le hash du jeton d'invitation est conservé : le lien n'est affiché qu'une fois, à la création.

## Décisions architecturales

Décisions durables qui s'appliquent à toutes les phases :

- **Routes frontend** : page unique `/profil/:username`. Alias `me` et `moi` vers le membre connecté. Sections sélectionnées par le paramètre `?section=` (publications, projets, contributions, dev, entreprise). Anciennes routes conservées comme redirections permanentes : `/forum/profil/:id`, `/forum/u/:username`, `/hub/profiles/:userId`, `/marketplace/profiles/:id`.
- **Routes API** : la résolution d'un profil se fait par nom d'utilisateur (famille `/api/v1/membres/u/<username>`, déjà existante). Les endpoints par identifiant numérique restent disponibles pour la compatibilité. Les réponses qui servent à construire un lien exposent `username`.
- **Identifiant** : `username`, unique sans tenir compte de la casse (contrainte sur la forme minuscule). La clé primaire des utilisateurs reste l'entier existant ; aucun UUID.
- **Noms réservés** : liste centralisée (`me`, `moi`, `admin`, `settings`, `new`, etc.), vérifiée à la création, au changement de nom et par la migration.
- **Modèle clé `Profil`** : un seul modèle avec un champ `type` (`dev` ou `entreprise`). FK vers l'utilisateur (à la place du `OneToOne`). Unicité sur `(user, type)`. Le type `entreprise` exige une entreprise ; le type `dev` n'en a pas (contrainte en base dans les deux sens).
- **Rattachement** : `Candidature`, `ProfilSkill`, `Experience`, `Prestation`, `Availability`, `Review`, `Connection` et `Swipe(network)` pointent vers un profil `dev`. `Offer.recruiter` pointe vers un profil `entreprise`. `Swipe(recruit)` va d'un profil `entreprise` vers un profil `dev`. Les contrôles sont faits côté serveur.
- **Entreprise** : une entreprise par membre. Création = devenir propriétaire. Rattachement uniquement par invitation (nouveau modèle `InvitationEntreprise` : entreprise, jeton, e-mail facultatif, statut, expiration, invitant, utilisateur accepté).
- **Visibilité** : toutes les routes de profil exigent d'être connecté. Le téléphone et l'e-mail de contact de l'entreprise ne sont exposés qu'aux membres de cette entreprise.
- **Compatibilité** : chaque phase laisse l'application fonctionnelle. Les services marketplace existants sont adaptés au type de profil dès la phase 4.
- **Vérifications** : les commandes de test et de build ne sont lancées que sur demande explicite de l'utilisateur (règle du dépôt) ; la dernière ligne de chaque phase indique ce qui n'a pas été vérifié.

---

## Phase 1 : nom d'utilisateur fiable

**User stories** : US-4, US-5, US-6.

### Ce qu'on livre

Un nom d'utilisateur désigne une seule personne, quelle que soit la casse, et ne peut pas être un nom réservé. Le membre qui change son nom est averti que ses anciens liens ne fonctionneront plus.

### Critères d'acceptation

- [ ] Créer ou modifier un utilisateur avec un nom qui ne diffère d'un existant que par la casse est refusé avec un message explicite.
- [ ] Un nom réservé est refusé à la création et au changement.
- [ ] La base interdit elle-même les doublons à la casse près.
- [ ] La mise à jour est refusée avec un rapport (comptes concernés) s'il existe déjà des doublons à la casse près ou des noms réservés.
- [ ] Le formulaire de modification du nom affiche l'avertissement sur les anciens liens avant la confirmation.
- [ ] La recherche par nom d'utilisateur ne renvoie plus un résultat arbitraire en cas d'homonymie de casse.

## Bloquée par

Aucune — démarrable immédiatement.

---

## Phase 2 : page de profil à /profil/:username

**User stories** : US-1, US-2, US-3, US-8, US-22, US-23.

### Ce qu'on livre

La page de profil existante s'ouvre à `/profil/<nom>` (insensible à la casse), avec les alias `me` et `moi`, les onglets Publications, Projets et Contributions, et le message « Profil introuvable » pour un nom inconnu ou désactivé. Un visiteur non connecté est invité à se connecter.

### Critères d'acceptation

- [ ] `/profil/<nom>` et `/profil/<NOM>` affichent la même page.
- [ ] `/profil/me` et `/profil/moi` mènent au profil du membre connecté (ou à la connexion s'il ne l'est pas).
- [ ] Un nom inexistant ou désactivé affiche « Profil introuvable ».
- [ ] Les onglets Publications, Projets et Contributions fonctionnent comme avant ; le paramètre `?section=` est conservé.
- [ ] La page n'utilise plus le mot « forum » dans son adresse ni dans son menu actif.

## Bloquée par

Phase 1.

---

## Phase 3 : anciennes adresses et liens internes

**User stories** : US-7.

### Ce qu'on livre

Les anciennes adresses du forum et du hub (`/forum/profil/:id`, `/forum/u/:username`, `/hub/profiles/:userId`) redirigent vers `/profil/<nom>` (avec le bon onglet quand le lien visait un contenu précis), et tous les liens internes (topbar, recherche, publications, messages, aperçus) pointent directement vers la nouvelle adresse.

### Critères d'acceptation

- [ ] `/forum/profil/<numéro>`, `/forum/u/<nom>` et `/hub/profiles/<numéro>` arrivent sur la bonne page de profil (la page du hub arrive sur l'onglet Projets).
- [ ] `/marketplace/profiles/<id>` est traité en phase 6 : cet identifiant est celui du profil marketplace, pas celui du membre, il ne peut donc rediriger qu'une fois l'onglet Profil dev en place.
- [ ] Un numéro inconnu affiche « Profil introuvable ».
- [ ] Plus aucun lien interne ne contient `/forum/profil/`.
- [ ] Les réponses d'API qui servaient à construire un lien exposent `username` (auteur de publication, membre suivi, interlocuteur d'un message, résultat de recherche).
- [ ] Le menu latéral met en avant la bonne entrée sur la nouvelle adresse.

## Bloquée par

Phase 2.

---

## Phase 4 : profil typé dev ou entreprise

**User stories** : US-24 (et prépare US-13).

### Ce qu'on livre

Un membre peut avoir un profil `dev` et un profil `entreprise`, jamais deux du même type. Les profils existants deviennent des profils `dev` ; ceux qui avaient une entreprise donnent aussi un profil `entreprise` rattaché à la même entreprise. Toutes les fonctions marketplace existantes continuent de marcher sur le profil `dev`.

### Critères d'acceptation

- [ ] Après migration, chaque ancien profil existe en profil `dev` avec les mêmes données.
- [ ] Chaque ancien profil rattaché à une entreprise a, en plus, un profil `entreprise` lié à la même entreprise (propriétaire si l'ancien l'était).
- [ ] La base interdit un second profil du même type pour un membre, un profil `entreprise` sans entreprise, et un profil `dev` avec une entreprise.
- [ ] Mon profil, mon CV, mes disponibilités, mes candidatures, l'annuaire des talents et le réseau fonctionnent sur le profil `dev`.
- [ ] Un membre qui n'a qu'un profil `entreprise` n'est pas listé dans l'annuaire des talents.
- [ ] La migration est réversible et laisse les données intactes en cas de retour arrière.

## Bloquée par

Aucune — peut démarrer en parallèle de la tranche A ; à intégrer avant la phase 5.

---

## Phase 5 : règles de rattachement des modèles liés

**User stories** : US-13, US-25.

### Ce qu'on livre

Chaque relation vers un profil n'accepte que le type prévu : les avis, connexions, candidatures, compétences, expériences, prestations et disponibilités vont à un profil `dev` ; les offres sont publiées par un profil `entreprise` ; les sélections de recrutement vont d'un profil `entreprise` vers un profil `dev`.

### Critères d'acceptation

- [ ] Un avis ou une connexion visant un profil `entreprise` est refusé avec un message explicite.
- [ ] Une candidature depuis un profil `entreprise` est refusée ; une offre dont le recruteur est un profil `dev` est refusée.
- [ ] Un swipe de recrutement dont l'auteur est un profil `dev` ou dont la cible est un profil `entreprise` est refusé ; un swipe de réseau entre deux profils `dev` est accepté.
- [ ] Les offres et candidatures existantes sont rattachées au bon profil après la migration, sans perte.
- [ ] Les listes (offres, candidatures, avis, connexions) ne mélangent jamais les deux profils d'un même membre.

## Bloquée par

Phase 4.

---

## Phase 6 : onglet Profil dev

**User stories** : US-9, US-10.

### Ce qu'on livre

La page de profil expose les profils du membre dans sa réponse et affiche un onglet **Profil dev** (compétences, expériences, prestations, disponibilités, avis, CV) quand il existe. Sur son propre profil, un membre sans profil dev peut en créer un.

### Critères d'acceptation

- [ ] L'onglet Profil dev apparaît pour un membre qui a un profil dev, et pas pour un autre.
- [ ] Il présente compétences, expériences, prestations, disponibilités, avis publics et lien vers le CV.
- [ ] Sur son propre profil, un membre sans profil dev voit une invitation à en créer un ; l'onglet apparaît après la création.
- [ ] Le CV respecte la visibilité existante (public, entreprises, privé).
- [ ] L'ancienne page de profil marketplace n'est plus qu'une redirection vers cet onglet.

## Bloquée par

Phase 3 et phase 5.

---

## Phase 7 : onglet Entreprise

**User stories** : US-11, US-12, US-20, US-21.

### Ce qu'on livre

Un onglet **Entreprise** présente la société (nom, secteur, taille, pays, description, badge « vérifiée ») et les offres publiées par le profil entreprise, quand il existe. Les coordonnées sensibles ne sont visibles que pour les membres de la société.

### Critères d'acceptation

- [ ] L'onglet Entreprise apparaît pour un membre qui a un profil entreprise, et pas pour un autre.
- [ ] Il affiche la société, le badge de vérification et les offres publiées par ce profil, et jamais de candidatures, compétences ni expériences.
- [ ] Le téléphone et l'e-mail de contact sont absents de la réponse pour un membre extérieur à la société et présents pour ses membres.
- [ ] Tout membre connecté voit l'onglet Entreprise d'un autre membre.
- [ ] L'onglet Profil dev d'un membre ne montre jamais ses offres.

## Bloquée par

Phase 6.

---

## Phase 8 : créer une entreprise

**User stories** : US-14, US-19.

### Ce qu'on livre

Un membre sans entreprise crée une entreprise depuis son profil, en devient propriétaire, et obtient un profil entreprise. Un membre déjà rattaché à une entreprise en est informé et ne peut pas en créer ou rejoindre une seconde.

### Critères d'acceptation

- [ ] Créer une entreprise crée la société et un profil entreprise propriétaire pour ce membre, et l'onglet Entreprise apparaît.
- [ ] Un membre qui a déjà un profil entreprise voit un message explicite et la création est refusée.
- [ ] Le nom de l'entreprise génère une adresse publique unique (même collision → suffixe).
- [ ] Une entreprise nouvellement créée n'est pas vérifiée ; le badge n'apparaît pas.
- [ ] Le propriétaire peut modifier les informations de sa société ; un membre simple non propriétaire ne le peut pas.

## Bloquée par

Phase 7.

---

## Phase 9 : inviter dans l'entreprise

**User stories** : US-15, US-17.

### Ce qu'on livre

Le propriétaire invite une personne par lien ou par e-mail, voit les invitations en attente et peut révoquer. Une invitation est à usage unique et expire.

### Critères d'acceptation

- [ ] Le propriétaire génère une invitation (lien, avec e-mail facultatif) et la voit dans la liste des invitations en attente de sa société.
- [ ] Une invitation avec e-mail envoie un message contenant le lien.
- [ ] Le propriétaire révoque une invitation en attente ; elle n'est plus utilisable.
- [ ] Un membre non propriétaire ne peut ni créer ni révoquer d'invitation.
- [ ] Une invitation expire après la durée fixée.

## Bloquée par

Phase 8.

---

## Phase 10 : rejoindre une entreprise par invitation

**User stories** : US-16, US-18.

### Ce qu'on livre

La personne invitée ouvre le lien, accepte, et obtient un profil entreprise rattaché à la société. Un lien expiré, révoqué, déjà utilisé, ou un invité déjà rattaché à une entreprise affiche un motif précis.

### Critères d'acceptation

- [ ] Accepter une invitation valide crée un profil entreprise (non propriétaire) pour l'invité, et l'invitation passe à « acceptée ».
- [ ] Ouvrir le lien d'une invitation expirée, révoquée ou déjà utilisée affiche le motif précis, sans rien créer.
- [ ] Un membre déjà rattaché à une entreprise ne peut pas accepter une autre invitation (message explicite).
- [ ] Un visiteur non connecté est dirigé vers la connexion puis revient sur l'invitation.
- [ ] Le propriétaire voit la personne ajoutée parmi les membres de la société.

## Bloquée par

Phase 9.
