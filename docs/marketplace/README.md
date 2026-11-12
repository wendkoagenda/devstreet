# Modèles de la marketplace DevStreet

Chaque fichier JSON décrit les attributs propres d'un modèle. Les clés étrangères et relations n'y figurent pas : elles sont décrites ici.

## Conventions

- Tous les modèles ont aussi `id` (UUID), `created_at` et `updated_at`, non répétés dans les JSON.
- Les types correspondent aux champs Django (`CharField`, `DecimalField`, etc.). `VectorField` vient de `pgvector`.
- `required: false` signifie `null=True, blank=True`.
- Champs calculés, non stockés : `User.reputation` (service commun DevStreet) et `Profil.available_from` (déduit du calendrier `Availability`).

## Relations

| De | Vers | Cardinalité | Implémentation Django | Remarque |
| --- | --- | --- | --- | --- |
| User | Profil | 1 - 1 | `Profil.user = OneToOneField(User)` | Un compte, un profil marketplace |
| Company | Profil | 0..1 - 1..n | `Profil.company = ForeignKey(Company, null=True)` | Recruteurs d'une entreprise ; `is_company_owner` marque le propriétaire |
| Company | Offer | 1 - 0..n | `Offer.company = ForeignKey(Company)` | |
| Profil | Offer | 1 - 0..n | `Offer.created_by = ForeignKey(Profil)` | Recruteur auteur de l'offre |
| Offer | Profil | 0..n - 0..n | `Offer.candidates = ManyToManyField(Profil, through="Candidature")` | Pivot **Candidature** : `unique_together = (offer, profil)` |
| Offer | Skill | 0..n - 0..n | `Offer.required_skills = ManyToManyField(Skill)` | Compétences requises, utilisées par le moteur de recommandation |
| Profil | Skill | 0..n - 0..n | `Profil.skills = ManyToManyField(Skill, through="ProfilSkill")` | Pivot **ProfilSkill** : `unique_together = (profil, skill)` |
| Skill | Tag du forum | 0..1 - 0..1 | `Skill.forum_tag = OneToOneField("forum.Tag", null=True)` | Partage des compétences avec l'espace forum |
| Profil | Experience | 1 - 0..n | `Experience.profil = ForeignKey(Profil)` | |
| Profil | Prestation | 1 - 0..n | `Prestation.profil = ForeignKey(Profil)` | |
| Profil | ProfilHistory | 1 - 0..n | `ProfilHistory.profil = ForeignKey(Profil)` | |
| User | ProfilHistory | 1 - 0..n | `ProfilHistory.changed_by = ForeignKey(User, null=True)` | Auteur de la modification |
| Profil | Availability | 1 - 0..n | `Availability.profil = ForeignKey(Profil)` | Une candidature acceptée crée une période `busy` (`source = mission`) |
| Profil | Review | 1 - 0..n | `Review.target = ForeignKey(Profil)` | Profil noté |
| Profil | Review | 1 - 0..n | `Review.author = ForeignKey(Profil)` | Profil qui note |
| Candidature | Review | 1 - 0..2 | `Review.candidature = ForeignKey(Candidature, null=True)` | Un avis dans chaque sens par mission |
| Profil | Swipe | 1 - 0..n | `Swipe.author = ForeignKey(Profil)` | Profil qui swipe |
| Profil | Swipe | 1 - 0..n | `Swipe.target = ForeignKey(Profil)` | Profil swipé ; `unique_together = (author, target, context)` |
| Profil | Connection | 1 - 0..n | `Connection.profil_a` et `Connection.profil_b = ForeignKey(Profil)` | Créée par un like mutuel en contexte `network` ; `unique_together = (profil_a, profil_b)` |

## Règles métier liées aux relations

- Un profil ne peut postuler qu'une fois par offre (contrainte d'unicité de Candidature).
- Le vivier d'une entreprise se lit depuis les Swipe `like` en contexte `recruit` de ses recruteurs.
- Chaque modification d'un Profil (ou de ses Experience et ProfilSkill) crée une ligne ProfilHistory et déclenche le recalcul de `Profil.embedding`.
- Le CV automatique est construit à la demande depuis Profil, ProfilSkill, Experience, Prestation et les Review publiques.
