# Module DevStreet Hub

- Package Python : `app.devstreet_hub`. Le label Django historique `projects` et les tables sont conservés pour maintenir la compatibilité des migrations déjà appliquées ; ne pas les renommer par simple remplacement de texte.

- Réutiliser `core.User`, `Role`, `Permission`, `has_permission` et l'authentification du core. Aucun nouvel endpoint de connexion ni système de rôles concurrent.
- `Project`, `Technology`, `ContributionTask` proviennent du générateur de la boilerplate ; les workflows les spécialisent. Ne pas régénérer après spécialisation sans revue des différences.
- Le code du générateur et ses templates ne sont pas modifiés pour les besoins métier.
- Les routes exposées sont enregistrées dans `urls.py`. Les anciens ViewSets CRUD générés pour Project/ContributionTask sont remplacés par les workflows ; aucun CRUD interne pour les snapshots, identités ou analyses.
- Règles métier dans les services ; accès ORM dans les repositories. Les vues et serializers adaptent les contrats HTTP.
- Le frontend est hors périmètre de cette étape. Après validation backend, décrire chaque interface dans un fichier Markdown numéroté.
- Vérifications : `python manage.py test app.tests.test_project app.tests.test_technology app.tests.test_contributiontask app.tests.test_devstreet_hub_integrations app.tests.test_devstreet_hub_rename`, puis suite backend et contrôles de la boilerplate.
