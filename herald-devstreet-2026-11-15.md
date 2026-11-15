# Rapport Herald — devstreet

_Analysé le 15/11/2026 · 5000 fichiers · 5 langages · 9934 problèmes_

_Généré par Async Herald 0.1.4 : analyse faite sur la machine, sans IA._

## Note

C- — 61/100

## Par catégorie

- Sécurité : 91/100 · 69 problèmes
- Qualité : 91/100 · 9405 problèmes
- Versioning : 100/100 · 3 problèmes
- DevOps : 88/100 · 44 problèmes
- Pattern : 100/100 · 397 problèmes
- Dépendances : 91/100 · 11 problèmes
- Tests : 100/100 · 5 problèmes

## Problèmes

### Secret affiché dans les journaux du pipeline — Critique ×4

Règle workflow-secret-in-run : Un echo d'un secret peut l'écrire dans les journaux du job, lisibles par d'autres personnes.

Comment corriger : N'affichez jamais un secret ; passez-le en variable d'environnement à la commande qui en a besoin.

- .github/workflows/ci-backend.yml:75
- .github/workflows/ci-backend.yml:76
- .github/workflows/ci-backend.yml:77
- .github/workflows/ci-backend.yml:78

### Dépendance avec une faille connue — Critique ×3

Règle vulnerable-dependency : La version utilisée de ce paquet a une vulnérabilité publiée (CVE ou avis GitHub). Les failles publiées sont les premières exploitées.

Comment corriger : Passez à la version corrigée indiquée, puis relancez vos tests.

- backend/requirements.txt
- backend/requirements.txt
- backend/requirements.txt

### Jeton d'accès en clair — Critique ×3

Règle leaked-secret : Un jeton reconnu (GitHub, AWS, Slack, Stripe, ou des identifiants dans une URL) est dans le code. Des robots parcourent les dépôts publics pour les récupérer en quelques minutes.

Comment corriger : Révoquez le jeton tout de suite chez le fournisseur, puis passez par une variable d'environnement.

- backend/scripts/security_scan/rules/secret_rules.py:33
- backend/venv/Lib/site-packages/httpx/_urls.py:16
- backend/venv/Lib/site-packages/httpx/_urls.py:328

### Déclaration avec var — Attention ×1410

Règle no_var : var a une portée surprenante (toute la fonction) qui provoque des bugs difficiles à trouver.

Comment corriger : Utilisez const, ou let si la valeur change.

- backend/venv/Lib/site-packages/drf_yasg/static/drf-yasg/immutable.js:12
- backend/venv/Lib/site-packages/drf_yasg/static/drf-yasg/immutable.js:76
- backend/venv/Lib/site-packages/drf_yasg/static/drf-yasg/immutable.js:77
- backend/venv/Lib/site-packages/drf_yasg/static/drf-yasg/immutable.js:78
- backend/venv/Lib/site-packages/drf_yasg/static/drf-yasg/immutable.js:79
- backend/venv/Lib/site-packages/drf_yasg/static/drf-yasg/immutable.js:82
- backend/venv/Lib/site-packages/drf_yasg/static/drf-yasg/immutable.js:85
- backend/venv/Lib/site-packages/drf_yasg/static/drf-yasg/immutable.js:86
- backend/venv/Lib/site-packages/drf_yasg/static/drf-yasg/immutable.js:87
- backend/venv/Lib/site-packages/drf_yasg/static/drf-yasg/immutable.js:91
- backend/venv/Lib/site-packages/drf_yasg/static/drf-yasg/immutable.js:94
- backend/venv/Lib/site-packages/drf_yasg/static/drf-yasg/immutable.js:95
- backend/venv/Lib/site-packages/drf_yasg/static/drf-yasg/immutable.js:114
- backend/venv/Lib/site-packages/drf_yasg/static/drf-yasg/immutable.js:115
- backend/venv/Lib/site-packages/drf_yasg/static/drf-yasg/immutable.js:116
- backend/venv/Lib/site-packages/drf_yasg/static/drf-yasg/immutable.js:138
- backend/venv/Lib/site-packages/drf_yasg/static/drf-yasg/immutable.js:176
- backend/venv/Lib/site-packages/drf_yasg/static/drf-yasg/immutable.js:177
- backend/venv/Lib/site-packages/drf_yasg/static/drf-yasg/immutable.js:178
- backend/venv/Lib/site-packages/drf_yasg/static/drf-yasg/immutable.js:180
- backend/venv/Lib/site-packages/drf_yasg/static/drf-yasg/immutable.js:181
- backend/venv/Lib/site-packages/drf_yasg/static/drf-yasg/immutable.js:183
- backend/venv/Lib/site-packages/drf_yasg/static/drf-yasg/immutable.js:207
- backend/venv/Lib/site-packages/drf_yasg/static/drf-yasg/immutable.js:227
- backend/venv/Lib/site-packages/drf_yasg/static/drf-yasg/immutable.js:232
- backend/venv/Lib/site-packages/drf_yasg/static/drf-yasg/immutable.js:353
- backend/venv/Lib/site-packages/drf_yasg/static/drf-yasg/immutable.js:370
- backend/venv/Lib/site-packages/drf_yasg/static/drf-yasg/immutable.js:371
- backend/venv/Lib/site-packages/drf_yasg/static/drf-yasg/immutable.js:372
- backend/venv/Lib/site-packages/drf_yasg/static/drf-yasg/immutable.js:381
- … et 1380 autres

### Ligne trop longue — Attention ×1033

Règle long-line : Une ligne très longue oblige à défiler horizontalement et se lit mal, surtout dans une revue de code.

Comment corriger : Coupez la ligne. Un formateur automatique (rustfmt, Prettier, Black) le fait pour vous.

- .github/workflows/cd-build-images.yml:11
- .github/workflows/cd-build-images.yml:57
- .github/workflows/cd-build-images.yml:61
- .github/workflows/cd-deploiement-gcp.yml:4
- .github/workflows/cd-deploiement-gcp.yml:7
- .github/workflows/cd-deploiement-ssh.yml:5
- .github/workflows/cd-gitea-ssh.yml:4
- .github/workflows/cd-gitea-ssh.yml:51
- .github/workflows/cd-gitea-ssh.yml:170
- .github/workflows/cd-gitea-ssh.yml:173
- .github/workflows/cd-gitea-ssh.yml:178
- .github/workflows/cd-maintenance.yml:75
- .github/workflows/cd-maintenance.yml:105
- .github/workflows/cd-maintenance.yml:169
- .github/workflows/cd-maintenance.yml:260
- .github/workflows/cd-maintenance.yml:448
- .github/workflows/cd-maintenance.yml:660
- .github/workflows/cd-minio-ssh.yml:58
- .github/workflows/cd-minio-ssh.yml:196
- .github/workflows/cd-observabilite-ssh.yml:60
- .github/workflows/cd-observabilite-ssh.yml:198
- .github/workflows/cd-orchestrateur.yml:59
- .github/workflows/cd-orchestrateur.yml:64
- .github/workflows/cd-orchestrateur.yml:76
- .github/workflows/cd-orchestrateur.yml:86
- .github/workflows/cd-orchestrateur.yml:119
- .github/workflows/cd-verifier-environnement.yml:32
- .github/workflows/ci-backend.yml:86
- .github/workflows/ci-backend.yml:93
- .github/workflows/ci-non-regression.yml:121
- … et 1003 autres

### Import inutilisé — Attention ×899

Règle unused-import : L'import n'est utilisé nulle part dans le fichier. Il encombre et peut alourdir le programme.

Comment corriger : Supprimez-le.

- backend/app/ai/providers/__init__.py:1
- backend/app/ai/repositories/__init__.py:1
- backend/app/ai/services/__init__.py:1
- backend/app/ai/views/__init__.py:1
- backend/app/communaute/admin.py:1
- backend/app/communaute/interfaces/avischoix_repository_interface.py:5
- backend/app/communaute/interfaces/commentaire_repository_interface.py:5
- backend/app/communaute/interfaces/confirmationaide_repository_interface.py:5
- backend/app/communaute/interfaces/conversation_repository_interface.py:5
- backend/app/communaute/interfaces/espace_repository_interface.py:5
- backend/app/communaute/interfaces/imagepublication_repository_interface.py:5
- backend/app/communaute/interfaces/lieninvitation_repository_interface.py:5
- backend/app/communaute/interfaces/likecommentaire_repository_interface.py:5
- backend/app/communaute/interfaces/likepublication_repository_interface.py:5
- backend/app/communaute/interfaces/message_repository_interface.py:5
- backend/app/communaute/interfaces/notificationresume_repository_interface.py:5
- backend/app/communaute/interfaces/optionpublication_repository_interface.py:5
- backend/app/communaute/interfaces/participationespace_repository_interface.py:5
- backend/app/communaute/interfaces/publication_repository_interface.py:5
- backend/app/communaute/interfaces/suiviutilisateur_repository_interface.py:5
- backend/app/communaute/interfaces/votesondage_repository_interface.py:5
- backend/app/communaute/management/commands/seed_avischoix.py:7
- backend/app/communaute/management/commands/seed_commentaire.py:7
- backend/app/communaute/management/commands/seed_confirmationaide.py:7
- backend/app/communaute/management/commands/seed_conversation.py:7
- backend/app/communaute/management/commands/seed_espace.py:7
- backend/app/communaute/management/commands/seed_imagepublication.py:7
- backend/app/communaute/management/commands/seed_likecommentaire.py:7
- backend/app/communaute/management/commands/seed_likepublication.py:7
- backend/app/communaute/management/commands/seed_optionpublication.py:7
- … et 869 autres

### Fonction trop complexe — Attention ×790

Règle high-complexity : La fonction a beaucoup de chemins possibles (conditions, boucles) : il faut beaucoup de tests pour tous les couvrir et les bugs s'y cachent facilement.

Comment corriger : Extrayez des sous-fonctions et simplifiez les conditions.

- .agents/skills/illustre/references/render_excalidraw.py:56
- backend/app/ai/providers/openai_compatible.py:46
- backend/app/communaute/management/commands/seed_forum_demo.py:227
- backend/app/communaute/services/commentaire_service.py:88
- backend/app/communaute/services/confirmationaide_service.py:118
- backend/app/communaute/services/espace_service.py:56
- backend/app/communaute/services/espace_service.py:639
- backend/app/communaute/services/project_topics.py:21
- backend/app/communaute/services/publication_service.py:142
- backend/app/communaute/services/publication_service.py:652
- backend/app/communaute/services/tag_service.py:88
- backend/app/communaute/views/publication_viewset.py:141
- backend/app/communaute/views/publication_viewset.py:287
- backend/app/communaute/views/publication_viewset.py:641
- backend/app/core/services/access_policy.py:89
- backend/app/core/services/oauth_service.py:126
- backend/app/core/services/oauth_service.py:168
- backend/app/core/services/oauth_service.py:257
- backend/app/core/services/user_service.py:122
- backend/app/core/views/auth_views.py:358
- backend/app/devstreet_hub/management/commands/seed_devstreet_hub_demo.py:70
- backend/app/devstreet_hub/services/analysis_worker.py:14
- backend/app/devstreet_hub/services/git_auth_service.py:159
- backend/app/devstreet_hub/services/git_auth_service.py:255
- backend/app/devstreet_hub/services/git_oauth_service.py:102
- backend/app/devstreet_hub/services/git_oauth_service.py:242
- backend/app/devstreet_hub/services/gitea_client.py:35
- backend/app/devstreet_hub/services/gitea_client.py:134
- backend/app/devstreet_hub/services/gitea_client.py:462
- backend/app/devstreet_hub/services/integration_service.py:26
- … et 760 autres

### Fonction difficile à suivre — Attention ×749

Règle high-cognitive-complexity : L'enchaînement des conditions et des imbrications demande trop d'effort pour être compris d'une seule lecture.

Comment corriger : Aplatissez avec des retours anticipés et extrayez les parties imbriquées.

- .agents/skills/illustre/references/render_excalidraw.py:56
- backend/app/communaute/management/commands/seed_forum_demo.py:227
- backend/app/communaute/management/commands/seed_forum_demo.py:288
- backend/app/communaute/services/commentaire_service.py:88
- backend/app/communaute/services/tag_service.py:88
- backend/app/communaute/views/publication_viewset.py:141
- backend/app/core/services/oauth_service.py:168
- backend/app/core/services/user_service.py:122
- backend/app/devstreet_hub/management/commands/seed_devstreet_hub_demo.py:70
- backend/app/devstreet_hub/services/git_auth_service.py:255
- backend/app/devstreet_hub/services/git_oauth_service.py:242
- backend/app/devstreet_hub/services/gitea_client.py:462
- backend/app/devstreet_hub/services/workflow_service.py:174
- backend/app/devstreet_hub/services/workflow_service.py:217
- backend/app/devstreet_hub/services/workflow_service.py:409
- backend/app/devstreet_hub/services/workflow_service.py:694
- backend/app/devstreet_hub/services/workflow_service.py:1130
- backend/app/marketplace/serializers.py:186
- backend/app/marketplace/serializers.py:430
- backend/app/marketplace/services/cv_service.py:381
- backend/app/marketplace/services/network_service.py:153
- backend/app/marketplace/services/offer_ai_service.py:86
- backend/app/marketplace/services/offer_ai_service.py:114
- backend/scripts/dependency_audit/audit.py:147
- backend/scripts/deploy_env/render.py:46
- backend/scripts/deploy_env/render_minio.py:31
- backend/scripts/deploy_env/render_observabilite.py:29
- backend/scripts/deploy_env/spec.py:215
- backend/scripts/deploy_env/spec.py:259
- backend/scripts/generate_api.py:47
- … et 719 autres

### Trop de paramètres — Attention ×563

Règle too-many-params : Avec beaucoup de paramètres, on confond facilement leur ordre et chaque appel devient difficile à lire.

Comment corriger : Regroupez les paramètres liés dans un objet ou une struct.

- backend/app/ai/providers/openai_compatible.py:18
- backend/app/ai/repositories/chat_repository.py:20
- backend/app/ai/services/chat_service.py:124
- backend/app/communaute/interfaces/publication_repository_interface.py:16
- backend/app/communaute/repositories/publication_repository.py:19
- backend/app/communaute/services/commentaire_service.py:88
- backend/app/communaute/services/espace_service.py:56
- backend/app/communaute/services/espace_service.py:247
- backend/app/communaute/services/espace_service.py:301
- backend/app/communaute/services/espace_service.py:403
- backend/app/communaute/services/project_topics.py:21
- backend/app/communaute/services/publication_service.py:56
- backend/app/communaute/services/publication_service.py:142
- backend/app/communaute/services/publication_service.py:513
- backend/app/communaute/services/publication_service.py:567
- backend/app/communaute/services/publication_service.py:614
- backend/app/communaute/services/publication_service.py:652
- backend/app/communaute/services/tag_service.py:174
- backend/app/core/services/audit_service.py:52
- backend/app/core/services/email_catalog.py:133
- backend/app/core/services/oauth_service.py:329
- backend/app/devstreet_hub/services/gitea_client.py:59
- backend/app/devstreet_hub/services/gitea_client.py:402
- backend/app/devstreet_hub/services/workflow_service.py:1031
- backend/app/marketplace/services/cv_service.py:271
- backend/app/marketplace/services/cv_service.py:280
- backend/scripts/build_devstreet_hub_postman.py:10
- backend/scripts/deploy_env/render.py:46
- backend/scripts/generate_api.py:365
- backend/scripts/generator/code_generator.py:304
- … et 533 autres

### Fonction trop longue — Attention ×562

Règle function-too-long : Une fonction longue fait plusieurs choses à la fois : elle est difficile à comprendre, à tester et à modifier sans casser autre chose.

Comment corriger : Découpez-la en petites fonctions qui ont chacune un nom clair.

- .agents/skills/illustre/references/render_excalidraw.py:56
- backend/app/ai/services/chat_service.py:61
- backend/app/communaute/management/commands/seed_avischoix.py:16
- backend/app/communaute/management/commands/seed_commentaire.py:16
- backend/app/communaute/management/commands/seed_confirmationaide.py:16
- backend/app/communaute/management/commands/seed_conversation.py:16
- backend/app/communaute/management/commands/seed_espace.py:16
- backend/app/communaute/management/commands/seed_forum_demo.py:80
- backend/app/communaute/management/commands/seed_forum_demo.py:173
- backend/app/communaute/management/commands/seed_forum_demo.py:227
- backend/app/communaute/management/commands/seed_imagepublication.py:16
- backend/app/communaute/management/commands/seed_lieninvitation.py:16
- backend/app/communaute/management/commands/seed_likecommentaire.py:16
- backend/app/communaute/management/commands/seed_likepublication.py:16
- backend/app/communaute/management/commands/seed_message.py:16
- backend/app/communaute/management/commands/seed_notificationresume.py:16
- backend/app/communaute/management/commands/seed_optionpublication.py:16
- backend/app/communaute/management/commands/seed_participationespace.py:16
- backend/app/communaute/management/commands/seed_publication.py:16
- backend/app/communaute/management/commands/seed_suiviutilisateur.py:16
- backend/app/communaute/management/commands/seed_votesondage.py:16
- backend/app/communaute/services/commentaire_service.py:88
- backend/app/communaute/services/espace_service.py:56
- backend/app/communaute/services/espace_service.py:162
- backend/app/communaute/services/espace_service.py:729
- backend/app/communaute/services/publication_service.py:87
- backend/app/communaute/services/publication_service.py:142
- backend/app/communaute/services/publication_service.py:304
- backend/app/communaute/services/publication_service.py:652
- backend/app/communaute/views/espace_viewset.py:300
- … et 532 autres

### Affichage de débogage oublié — Attention ×560

Règle no_debug_print : Un print, console.log ou dbg! oublié pollue les journaux et peut afficher des données sensibles.

Comment corriger : Supprimez-le, ou remplacez-le par un vrai journal (logger) avec un niveau adapté.

- .agents/skills/illustre/references/render_excalidraw.py:262
- .agents/skills/illustre/references/render_excalidraw.py:263
- .agents/skills/illustre/references/render_excalidraw.py:269
- .agents/skills/illustre/references/render_excalidraw.py:277
- .agents/skills/illustre/references/render_excalidraw.py:279
- backend/config/settings.py:268
- backend/config/settings.py:273
- backend/scripts/build_devstreet_hub_postman.py:382
- backend/scripts/create_app_template.py:402
- backend/scripts/create_app_template.py:403
- backend/scripts/create_app_template.py:404
- backend/scripts/create_app_template.py:405
- backend/scripts/create_app_template.py:406
- backend/scripts/create_app_template.py:407
- backend/scripts/create_app_template.py:408
- backend/scripts/create_app_template.py:412
- backend/scripts/dependency_audit/cli.py:30
- backend/scripts/dependency_audit/cli.py:40
- backend/scripts/dependency_audit/cli.py:47
- backend/scripts/dependency_audit/cli.py:48
- backend/scripts/deploy_env/render.py:145
- backend/scripts/deploy_env/render.py:150
- backend/scripts/deploy_env/render.py:152
- backend/scripts/deploy_env/render.py:158
- backend/scripts/deploy_env/render_gitea.py:70
- backend/scripts/deploy_env/render_gitea.py:75
- backend/scripts/deploy_env/render_gitea.py:77
- backend/scripts/deploy_env/render_gitea.py:83
- backend/scripts/deploy_env/render_minio.py:102
- backend/scripts/deploy_env/render_minio.py:107
- … et 530 autres

### Paramètre inutilisé — Attention ×549

Règle unused-parameter : Le paramètre est reçu mais jamais utilisé : les appelants passent une valeur pour rien.

Comment corriger : Supprimez-le, ou préfixez-le par _ s'il est imposé par une interface.

- backend/app/ai/providers/base.py:22
- backend/app/communaute/interfaces/avischoix_repository_interface.py:52
- backend/app/communaute/interfaces/commentaire_repository_interface.py:52
- backend/app/communaute/interfaces/confirmationaide_repository_interface.py:52
- backend/app/communaute/interfaces/conversation_repository_interface.py:52
- backend/app/communaute/interfaces/espace_repository_interface.py:52
- backend/app/communaute/interfaces/imagepublication_repository_interface.py:52
- backend/app/communaute/interfaces/lieninvitation_repository_interface.py:52
- backend/app/communaute/interfaces/likecommentaire_repository_interface.py:52
- backend/app/communaute/interfaces/likepublication_repository_interface.py:52
- backend/app/communaute/interfaces/message_repository_interface.py:52
- backend/app/communaute/interfaces/notificationresume_repository_interface.py:52
- backend/app/communaute/interfaces/optionpublication_repository_interface.py:52
- backend/app/communaute/interfaces/participationespace_repository_interface.py:52
- backend/app/communaute/interfaces/publication_repository_interface.py:60
- backend/app/communaute/interfaces/suiviutilisateur_repository_interface.py:52
- backend/app/communaute/interfaces/votesondage_repository_interface.py:52
- backend/app/communaute/views/avischoix_viewset.py:88
- backend/app/communaute/views/avischoix_viewset.py:214
- backend/app/communaute/views/commentaire_viewset.py:93
- backend/app/communaute/views/commentaire_viewset.py:228
- backend/app/communaute/views/confirmationaide_viewset.py:88
- backend/app/communaute/views/imagepublication_viewset.py:88
- backend/app/communaute/views/imagepublication_viewset.py:214
- backend/app/communaute/views/lieninvitation_viewset.py:88
- backend/app/communaute/views/lieninvitation_viewset.py:214
- backend/app/communaute/views/likecommentaire_viewset.py:88
- backend/app/communaute/views/likecommentaire_viewset.py:214
- backend/app/communaute/views/likepublication_viewset.py:88
- backend/app/communaute/views/likepublication_viewset.py:214
- … et 519 autres

### Code mis en commentaire — Attention ×445

Règle commented-out-code : Du code désactivé encombre le fichier et on ne sait plus s'il faut le garder. Git conserve déjà les anciennes versions.

Comment corriger : Supprimez-le.

- backend/app/communaute/services/publication_service.py:203
- backend/app/devstreet_hub/services/gitea_client.py:169
- backend/scripts/deploy_env/spec.py:86
- backend/venv/Lib/site-packages/PIL/BmpImagePlugin.py:47
- backend/venv/Lib/site-packages/PIL/EpsImagePlugin.py:264
- backend/venv/Lib/site-packages/PIL/EpsImagePlugin.py:298
- backend/venv/Lib/site-packages/PIL/EpsImagePlugin.py:457
- backend/venv/Lib/site-packages/PIL/FpxImagePlugin.py:145
- backend/venv/Lib/site-packages/PIL/FpxImagePlugin.py:151
- backend/venv/Lib/site-packages/PIL/IcoImagePlugin.py:115
- backend/venv/Lib/site-packages/PIL/IcoImagePlugin.py:120
- backend/venv/Lib/site-packages/PIL/IcoImagePlugin.py:121
- backend/venv/Lib/site-packages/PIL/IcoImagePlugin.py:124
- backend/venv/Lib/site-packages/PIL/IcoImagePlugin.py:125
- backend/venv/Lib/site-packages/PIL/IcoImagePlugin.py:126
- backend/venv/Lib/site-packages/PIL/IcoImagePlugin.py:127
- backend/venv/Lib/site-packages/PIL/IcoImagePlugin.py:147
- backend/venv/Lib/site-packages/PIL/IcoImagePlugin.py:148
- backend/venv/Lib/site-packages/PIL/IcoImagePlugin.py:387
- backend/venv/Lib/site-packages/PIL/Image.py:1202
- backend/venv/Lib/site-packages/PIL/Image.py:2032
- backend/venv/Lib/site-packages/PIL/ImageDraw.py:626
- backend/venv/Lib/site-packages/PIL/ImageFile.py:290
- backend/venv/Lib/site-packages/PIL/ImageFile.py:461
- backend/venv/Lib/site-packages/PIL/ImageFile.py:465
- backend/venv/Lib/site-packages/PIL/Jpeg2KImagePlugin.py:358
- backend/venv/Lib/site-packages/PIL/JpegImagePlugin.py:149
- backend/venv/Lib/site-packages/PIL/JpegImagePlugin.py:401
- backend/venv/Lib/site-packages/PIL/JpegImagePlugin.py:629
- backend/venv/Lib/site-packages/PIL/MicImagePlugin.py:60
- … et 415 autres

### Nom hors convention — Attention ×333

Règle naming-conventions : Ce nom ne suit pas l'usage du langage (camelCase, PascalCase, snake_case) : le code paraît incohérent.

Comment corriger : Renommez selon la convention du langage.

- backend/app/core/tests.py:23
- backend/app/core/tests.py:68
- backend/app/core/tests.py:133
- backend/app/core/tests.py:190
- backend/app/core/tests.py:251
- backend/app/core/tests.py:295
- backend/venv/Lib/site-packages/PIL/EpsImagePlugin.py:72
- backend/venv/Lib/site-packages/PIL/ImageCms.py:184
- backend/venv/Lib/site-packages/PIL/ImageCms.py:361
- backend/venv/Lib/site-packages/PIL/ImageCms.py:457
- backend/venv/Lib/site-packages/PIL/ImageCms.py:481
- backend/venv/Lib/site-packages/PIL/ImageCms.py:564
- backend/venv/Lib/site-packages/PIL/ImageCms.py:681
- backend/venv/Lib/site-packages/PIL/ImageCms.py:736
- backend/venv/Lib/site-packages/PIL/ImageCms.py:787
- backend/venv/Lib/site-packages/PIL/ImageCms.py:829
- backend/venv/Lib/site-packages/PIL/ImageCms.py:866
- backend/venv/Lib/site-packages/PIL/ImageCms.py:894
- backend/venv/Lib/site-packages/PIL/ImageCms.py:922
- backend/venv/Lib/site-packages/PIL/ImageCms.py:951
- backend/venv/Lib/site-packages/PIL/ImageCms.py:980
- backend/venv/Lib/site-packages/PIL/ImageCms.py:1019
- backend/venv/Lib/site-packages/PIL/ImageDraw.py:771
- backend/venv/Lib/site-packages/PIL/JpegImagePlugin.py:74
- backend/venv/Lib/site-packages/PIL/JpegImagePlugin.py:80
- backend/venv/Lib/site-packages/PIL/JpegImagePlugin.py:187
- backend/venv/Lib/site-packages/PIL/JpegImagePlugin.py:199
- backend/venv/Lib/site-packages/PIL/JpegImagePlugin.py:248
- backend/venv/Lib/site-packages/_pytest/assertion/rewrite.py:845
- backend/venv/Lib/site-packages/_pytest/assertion/rewrite.py:966
- … et 303 autres

### Bloc catch vide — Attention ×255

Règle empty-catch : L'erreur est attrapée puis ignorée : le programme continue comme si de rien n'était et le problème devient invisible.

Comment corriger : Journalisez l'erreur, traitez-la, ou laissez-la remonter.

- backend/venv/Lib/site-packages/PIL/EpsImagePlugin.py:178
- backend/venv/Lib/site-packages/PIL/EpsImagePlugin.py:257
- backend/venv/Lib/site-packages/PIL/GifImagePlugin.py:408
- backend/venv/Lib/site-packages/PIL/GifImagePlugin.py:731
- backend/venv/Lib/site-packages/PIL/IcnsImagePlugin.py:248
- backend/venv/Lib/site-packages/PIL/ImImagePlugin.py:274
- backend/venv/Lib/site-packages/PIL/Image.py:445
- backend/venv/Lib/site-packages/PIL/Image.py:451
- backend/venv/Lib/site-packages/PIL/Image.py:457
- backend/venv/Lib/site-packages/PIL/Image.py:463
- backend/venv/Lib/site-packages/PIL/Image.py:469
- backend/venv/Lib/site-packages/PIL/Image.py:491
- backend/venv/Lib/site-packages/PIL/Image.py:515
- backend/venv/Lib/site-packages/PIL/Image.py:540
- backend/venv/Lib/site-packages/PIL/Image.py:2719
- backend/venv/Lib/site-packages/PIL/Image.py:4103
- backend/venv/Lib/site-packages/PIL/Image.py:4328
- backend/venv/Lib/site-packages/PIL/ImageDraw.py:849
- backend/venv/Lib/site-packages/PIL/ImageFile.py:590
- backend/venv/Lib/site-packages/PIL/ImageFilter.py:414
- backend/venv/Lib/site-packages/PIL/ImageFont.py:135
- backend/venv/Lib/site-packages/PIL/ImageFont.py:959
- backend/venv/Lib/site-packages/PIL/ImagePalette.py:308
- backend/venv/Lib/site-packages/PIL/ImageShow.py:360
- backend/venv/Lib/site-packages/PIL/ImageTk.py:145
- backend/venv/Lib/site-packages/PIL/ImageTk.py:233
- backend/venv/Lib/site-packages/PIL/IptcImagePlugin.py:205
- backend/venv/Lib/site-packages/PIL/IptcImagePlugin.py:225
- backend/venv/Lib/site-packages/PIL/JpegImagePlugin.py:102
- backend/venv/Lib/site-packages/PIL/JpegImagePlugin.py:167
- … et 225 autres

### Erreur ignorée — Attention ×227

Règle swallowed-error : Une erreur est attrapée sans être traitée ni journalisée (except: pass, if err != nil {} vide, unwrap_or_default). Quand ça casse, rien ne permet de comprendre pourquoi.

Comment corriger : Journalisez l'erreur ou faites-la remonter à l'appelant.

- backend/venv/Lib/site-packages/PIL/EpsImagePlugin.py:178
- backend/venv/Lib/site-packages/PIL/EpsImagePlugin.py:257
- backend/venv/Lib/site-packages/PIL/GifImagePlugin.py:408
- backend/venv/Lib/site-packages/PIL/GifImagePlugin.py:731
- backend/venv/Lib/site-packages/PIL/IcnsImagePlugin.py:248
- backend/venv/Lib/site-packages/PIL/ImImagePlugin.py:274
- backend/venv/Lib/site-packages/PIL/Image.py:445
- backend/venv/Lib/site-packages/PIL/Image.py:451
- backend/venv/Lib/site-packages/PIL/Image.py:457
- backend/venv/Lib/site-packages/PIL/Image.py:463
- backend/venv/Lib/site-packages/PIL/Image.py:469
- backend/venv/Lib/site-packages/PIL/Image.py:491
- backend/venv/Lib/site-packages/PIL/Image.py:515
- backend/venv/Lib/site-packages/PIL/Image.py:540
- backend/venv/Lib/site-packages/PIL/Image.py:2713
- backend/venv/Lib/site-packages/PIL/Image.py:2719
- backend/venv/Lib/site-packages/PIL/Image.py:4103
- backend/venv/Lib/site-packages/PIL/Image.py:4328
- backend/venv/Lib/site-packages/PIL/ImageDraw.py:849
- backend/venv/Lib/site-packages/PIL/ImageFile.py:590
- backend/venv/Lib/site-packages/PIL/ImageFilter.py:414
- backend/venv/Lib/site-packages/PIL/ImageFont.py:135
- backend/venv/Lib/site-packages/PIL/ImageFont.py:959
- backend/venv/Lib/site-packages/PIL/ImagePalette.py:308
- backend/venv/Lib/site-packages/PIL/ImageShow.py:360
- backend/venv/Lib/site-packages/PIL/ImageTk.py:145
- backend/venv/Lib/site-packages/PIL/ImageTk.py:233
- backend/venv/Lib/site-packages/PIL/IptcImagePlugin.py:205
- backend/venv/Lib/site-packages/PIL/IptcImagePlugin.py:225
- backend/venv/Lib/site-packages/PIL/JpegImagePlugin.py:102
- … et 197 autres

### TODO ou FIXME oublié — Attention ×226

Règle todo_fixme : Ce marqueur signale un travail non terminé, qui a tendance à rester là indéfiniment.

Comment corriger : Faites le travail, ou créez un ticket et retirez le commentaire.

- backend/venv/Lib/site-packages/PIL/FontFile.py:147
- backend/venv/Lib/site-packages/PIL/FpxImagePlugin.py:184
- backend/venv/Lib/site-packages/PIL/FpxImagePlugin.py:222
- backend/venv/Lib/site-packages/PIL/GifImagePlugin.py:128
- backend/venv/Lib/site-packages/PIL/IcoImagePlugin.py:108
- backend/venv/Lib/site-packages/PIL/ImImagePlugin.py:161
- backend/venv/Lib/site-packages/PIL/ImImagePlugin.py:260
- backend/venv/Lib/site-packages/PIL/Image.py:634
- backend/venv/Lib/site-packages/PIL/Image.py:1909
- backend/venv/Lib/site-packages/PIL/Image.py:2045
- backend/venv/Lib/site-packages/PIL/Image.py:2923
- backend/venv/Lib/site-packages/PIL/ImageCms.py:1062
- backend/venv/Lib/site-packages/PIL/ImageDraw.py:99
- backend/venv/Lib/site-packages/PIL/ImageDraw.py:126
- backend/venv/Lib/site-packages/PIL/ImageDraw2.py:62
- backend/venv/Lib/site-packages/PIL/ImageFile.py:376
- backend/venv/Lib/site-packages/PIL/ImageFile.py:663
- backend/venv/Lib/site-packages/PIL/ImageFont.py:83
- backend/venv/Lib/site-packages/PIL/ImageFont.py:167
- backend/venv/Lib/site-packages/PIL/ImageFont.py:257
- backend/venv/Lib/site-packages/PIL/ImagePalette.py:257
- backend/venv/Lib/site-packages/PIL/ImagePalette.py:288
- backend/venv/Lib/site-packages/PIL/ImageQt.py:143
- backend/venv/Lib/site-packages/PIL/JpegImagePlugin.py:123
- backend/venv/Lib/site-packages/PIL/JpegImagePlugin.py:253
- backend/venv/Lib/site-packages/PIL/JpegImagePlugin.py:815
- backend/venv/Lib/site-packages/PIL/McIdasImagePlugin.py:57
- backend/venv/Lib/site-packages/PIL/MpoImagePlugin.py:135
- backend/venv/Lib/site-packages/PIL/MspImagePlugin.py:190
- backend/venv/Lib/site-packages/PIL/PSDraw.py:45
- … et 196 autres

### Fichier trop long — Attention ×212

Règle max_file_lines : Un fichier très long mélange souvent plusieurs sujets et devient difficile à parcourir.

Comment corriger : Répartissez son contenu dans plusieurs modules, un par sujet.

- .github/workflows/cd-maintenance.yml:1
- backend/app/communaute/migrations/0001_initial.py:1
- backend/app/communaute/models.py:1
- backend/app/communaute/serializers.py:1
- backend/app/communaute/services/espace_service.py:1
- backend/app/communaute/services/publication_service.py:1
- backend/app/communaute/views/espace_viewset.py:1
- backend/app/communaute/views/publication_viewset.py:1
- backend/app/core/views/auth_views.py:1
- backend/app/devstreet_hub/migrations/0001_initial.py:1
- backend/app/devstreet_hub/models.py:1
- backend/app/devstreet_hub/services/gitea_client.py:1
- backend/app/devstreet_hub/services/workflow_service.py:1
- backend/app/devstreet_hub/views/workflow_viewsets.py:1
- backend/app/marketplace/models.py:1
- backend/app/marketplace/serializers.py:1
- backend/app/marketplace/services/cv_service.py:1
- backend/scripts/generate_api.py:1
- backend/scripts/generator/code_generator.py:1
- backend/scripts/generator/frontend_generator.py:1
- backend/scripts/generator/state_manager.py:1
- backend/venv/Lib/site-packages/PIL/BlpImagePlugin.py:1
- backend/venv/Lib/site-packages/PIL/BmpImagePlugin.py:1
- backend/venv/Lib/site-packages/PIL/DdsImagePlugin.py:1
- backend/venv/Lib/site-packages/PIL/GifImagePlugin.py:1
- backend/venv/Lib/site-packages/PIL/Image.py:1
- backend/venv/Lib/site-packages/PIL/ImageCms.py:1
- backend/venv/Lib/site-packages/PIL/ImageDraw.py:1
- backend/venv/Lib/site-packages/PIL/ImageFile.py:1
- backend/venv/Lib/site-packages/PIL/ImageFilter.py:1
- … et 182 autres

### Principe de conception SOLID non respecté — Attention ×192

Règle solid : La classe ou le module mélange des responsabilités, ou dépend de détails qu'il devrait ignorer : il devient difficile à faire évoluer.

Comment corriger : Séparez les responsabilités et faites dépendre le code d'interfaces plutôt que d'implémentations.

- backend/venv/Lib/site-packages/django/contrib/admin/static/admin/js/core.js:60
- backend/venv/Lib/site-packages/django/contrib/admin/static/admin/js/core.js:64
- backend/venv/Lib/site-packages/django/contrib/admin/static/admin/js/core.js:68
- backend/venv/Lib/site-packages/django/contrib/admin/static/admin/js/core.js:72
- backend/venv/Lib/site-packages/django/contrib/admin/static/admin/js/core.js:76
- backend/venv/Lib/site-packages/django/contrib/admin/static/admin/js/core.js:80
- backend/venv/Lib/site-packages/django/contrib/admin/static/admin/js/core.js:84
- backend/venv/Lib/site-packages/django/contrib/admin/static/admin/js/core.js:88
- backend/venv/Lib/site-packages/django/contrib/admin/static/admin/js/core.js:94
- backend/venv/Lib/site-packages/django/contrib/admin/static/admin/js/core.js:100
- backend/venv/Lib/site-packages/django/contrib/admin/static/admin/js/core.js:106
- backend/venv/Lib/site-packages/django/contrib/admin/static/admin/js/core.js:112
- backend/venv/Lib/site-packages/django/contrib/admin/static/admin/js/core.js:150
- backend/venv/Lib/site-packages/drf_yasg/static/drf-yasg/immutable.js:18
- backend/venv/Lib/site-packages/drf_yasg/static/drf-yasg/immutable.js:190
- backend/venv/Lib/site-packages/drf_yasg/static/drf-yasg/immutable.js:199
- backend/venv/Lib/site-packages/drf_yasg/static/drf-yasg/immutable.js:200
- backend/venv/Lib/site-packages/drf_yasg/static/drf-yasg/immutable.js:255
- backend/venv/Lib/site-packages/drf_yasg/static/drf-yasg/immutable.js:259
- backend/venv/Lib/site-packages/drf_yasg/static/drf-yasg/immutable.js:263
- backend/venv/Lib/site-packages/drf_yasg/static/drf-yasg/immutable.js:273
- backend/venv/Lib/site-packages/drf_yasg/static/drf-yasg/immutable.js:279
- backend/venv/Lib/site-packages/drf_yasg/static/drf-yasg/immutable.js:294
- backend/venv/Lib/site-packages/drf_yasg/static/drf-yasg/immutable.js:311
- backend/venv/Lib/site-packages/drf_yasg/static/drf-yasg/immutable.js:315
- backend/venv/Lib/site-packages/drf_yasg/static/drf-yasg/immutable.js:319
- backend/venv/Lib/site-packages/drf_yasg/static/drf-yasg/immutable.js:323
- backend/venv/Lib/site-packages/drf_yasg/static/drf-yasg/immutable.js:342
- backend/venv/Lib/site-packages/drf_yasg/static/drf-yasg/immutable.js:365
- backend/venv/Lib/site-packages/drf_yasg/static/drf-yasg/immutable.js:369
- … et 162 autres

### Code trop imbriqué — Attention ×162

Règle deep-nesting : Plusieurs niveaux de if et de boucles imbriqués rendent le chemin d'exécution difficile à suivre.

Comment corriger : Sortez tôt avec des clauses de garde (if … return) et extrayez les blocs internes en fonctions.

- backend/app/core/services/oauth_service.py:168
- backend/app/devstreet_hub/services/workflow_service.py:1130
- backend/scripts/generator/code_generator.py:1176
- backend/scripts/generator/code_generator.py:1448
- backend/scripts/security_scan/rules/api_rules.py:119
- backend/scripts/security_scan/rules/django_rules.py:287
- backend/scripts/security_scan/rules/exposure_rules.py:36
- backend/venv/Lib/site-packages/PIL/AvifImagePlugin.py:151
- backend/venv/Lib/site-packages/PIL/BlpImagePlugin.py:69
- backend/venv/Lib/site-packages/PIL/BlpImagePlugin.py:390
- backend/venv/Lib/site-packages/PIL/BmpImagePlugin.py:334
- backend/venv/Lib/site-packages/PIL/EpsImagePlugin.py:49
- backend/venv/Lib/site-packages/PIL/EpsImagePlugin.py:201
- backend/venv/Lib/site-packages/PIL/GifImagePlugin.py:179
- backend/venv/Lib/site-packages/PIL/GifImagePlugin.py:545
- backend/venv/Lib/site-packages/PIL/GifImagePlugin.py:663
- backend/venv/Lib/site-packages/PIL/IcoImagePlugin.py:63
- backend/venv/Lib/site-packages/PIL/Image.py:1016
- backend/venv/Lib/site-packages/PIL/Image.py:4231
- backend/venv/Lib/site-packages/PIL/ImageDraw.py:237
- backend/venv/Lib/site-packages/PIL/ImageDraw.py:799
- backend/venv/Lib/site-packages/PIL/ImageFile.py:296
- backend/venv/Lib/site-packages/PIL/ImageFile.py:678
- backend/venv/Lib/site-packages/PIL/ImageFont.py:814
- backend/venv/Lib/site-packages/PIL/ImageGrab.py:34
- backend/venv/Lib/site-packages/PIL/ImageOps.py:745
- backend/venv/Lib/site-packages/PIL/ImageText.py:178
- backend/venv/Lib/site-packages/PIL/ImageText.py:328
- backend/venv/Lib/site-packages/PIL/Jpeg2KImagePlugin.py:156
- backend/venv/Lib/site-packages/PIL/MpoImagePlugin.py:47
- … et 132 autres

### Booléen inutile — Attention ×144

Règle redundant-boolean : Comparer à true ou renvoyer true/false selon une condition alourdit le code sans rien apporter.

Comment corriger : Utilisez la condition directement : if (x), return condition.

- backend/scripts/security_scan/rules/django_rules.py:56
- backend/scripts/security_scan/rules/django_rules.py:99
- backend/scripts/security_scan/rules/exposure_rules.py:99
- backend/scripts/security_scan/rules/python_rules.py:41
- backend/venv/Lib/site-packages/PIL/EpsImagePlugin.py:69
- backend/venv/Lib/site-packages/PIL/IcoImagePlugin.py:233
- backend/venv/Lib/site-packages/_pytest/assertion/rewrite.py:512
- backend/venv/Lib/site-packages/_pytest/main.py:650
- backend/venv/Lib/site-packages/_pytest/main.py:668
- backend/venv/Lib/site-packages/_pytest/nodes.py:435
- backend/venv/Lib/site-packages/_pytest/python.py:364
- backend/venv/Lib/site-packages/boolean/boolean.py:939
- backend/venv/Lib/site-packages/boolean/boolean.py:967
- backend/venv/Lib/site-packages/charset_normalizer/cli/__main__.py:185
- backend/venv/Lib/site-packages/charset_normalizer/cli/__main__.py:185
- backend/venv/Lib/site-packages/charset_normalizer/cli/__main__.py:192
- backend/venv/Lib/site-packages/charset_normalizer/cli/__main__.py:192
- backend/venv/Lib/site-packages/charset_normalizer/cli/__main__.py:213
- backend/venv/Lib/site-packages/charset_normalizer/cli/__main__.py:288
- backend/venv/Lib/site-packages/charset_normalizer/cli/__main__.py:289
- backend/venv/Lib/site-packages/charset_normalizer/cli/__main__.py:296
- backend/venv/Lib/site-packages/charset_normalizer/cli/__main__.py:305
- backend/venv/Lib/site-packages/charset_normalizer/cli/__main__.py:307
- backend/venv/Lib/site-packages/charset_normalizer/cli/__main__.py:310
- backend/venv/Lib/site-packages/charset_normalizer/cli/__main__.py:311
- backend/venv/Lib/site-packages/charset_normalizer/cli/__main__.py:319
- backend/venv/Lib/site-packages/charset_normalizer/cli/__main__.py:330
- backend/venv/Lib/site-packages/charset_normalizer/cli/__main__.py:334
- backend/venv/Lib/site-packages/charset_normalizer/cli/__main__.py:337
- backend/venv/Lib/site-packages/click/core.py:3015
- … et 114 autres

### Module trop dépendant — Attention ×109

Règle high-coupling : Ce module importe beaucoup d'autres modules : il casse dès que l'un d'eux change.

Comment corriger : Réduisez ses dépendances, par exemple en le découpant.

- backend/app/communaute/urls.py:1
- backend/app/communaute/views/publication_viewset.py:1
- backend/app/core/views/auth_views.py:1
- backend/app/devstreet_hub/services/workflow_service.py:1
- backend/scripts/smoke_git_computer_auth.py:1
- backend/venv/Lib/site-packages/PIL/Image.py:1
- backend/venv/Lib/site-packages/_pytest/assertion/rewrite.py:1
- backend/venv/Lib/site-packages/_pytest/cacheprovider.py:1
- backend/venv/Lib/site-packages/_pytest/capture.py:1
- backend/venv/Lib/site-packages/_pytest/config/__init__.py:1
- backend/venv/Lib/site-packages/_pytest/debugging.py:1
- backend/venv/Lib/site-packages/_pytest/doctest.py:1
- backend/venv/Lib/site-packages/_pytest/fixtures.py:1
- backend/venv/Lib/site-packages/_pytest/hookspec.py:1
- backend/venv/Lib/site-packages/_pytest/legacypath.py:1
- backend/venv/Lib/site-packages/_pytest/logging.py:1
- backend/venv/Lib/site-packages/_pytest/main.py:1
- backend/venv/Lib/site-packages/_pytest/mark/__init__.py:1
- backend/venv/Lib/site-packages/_pytest/mark/structures.py:1
- backend/venv/Lib/site-packages/_pytest/monkeypatch.py:1
- backend/venv/Lib/site-packages/_pytest/nodes.py:1
- backend/venv/Lib/site-packages/_pytest/pathlib.py:1
- backend/venv/Lib/site-packages/_pytest/pytester.py:1
- backend/venv/Lib/site-packages/_pytest/python.py:1
- backend/venv/Lib/site-packages/_pytest/python_api.py:1
- backend/venv/Lib/site-packages/_pytest/raises.py:1
- backend/venv/Lib/site-packages/click/__init__.py:1
- backend/venv/Lib/site-packages/click/_termui_impl.py:1
- backend/venv/Lib/site-packages/click/_winconsole.py:1
- backend/venv/Lib/site-packages/click/core.py:1
- … et 79 autres

### Import de tout un module (import *) — Attention ×56

Règle wildcard_import : from module import * ajoute des noms invisibles : on ne sait plus d'où vient une fonction, et des noms peuvent s'écraser.

Comment corriger : Importez explicitement les noms utilisés.

- backend/venv/Lib/site-packages/django/contrib/gis/db/models/__init__.py:1
- backend/venv/Lib/site-packages/django/contrib/gis/db/models/__init__.py:5
- backend/venv/Lib/site-packages/django/contrib/gis/forms/__init__.py:1
- backend/venv/Lib/site-packages/django/contrib/messages/__init__.py:1
- backend/venv/Lib/site-packages/django/contrib/messages/__init__.py:2
- backend/venv/Lib/site-packages/django/contrib/postgres/aggregates/__init__.py:1
- backend/venv/Lib/site-packages/django/contrib/postgres/aggregates/__init__.py:2
- backend/venv/Lib/site-packages/django/contrib/postgres/fields/__init__.py:1
- backend/venv/Lib/site-packages/django/contrib/postgres/fields/__init__.py:2
- backend/venv/Lib/site-packages/django/contrib/postgres/fields/__init__.py:3
- backend/venv/Lib/site-packages/django/contrib/postgres/fields/__init__.py:4
- backend/venv/Lib/site-packages/django/contrib/postgres/fields/__init__.py:5
- backend/venv/Lib/site-packages/django/contrib/postgres/forms/__init__.py:1
- backend/venv/Lib/site-packages/django/contrib/postgres/forms/__init__.py:2
- backend/venv/Lib/site-packages/django/contrib/postgres/forms/__init__.py:3
- backend/venv/Lib/site-packages/django/db/models/sql/__init__.py:1
- backend/venv/Lib/site-packages/django/db/models/sql/__init__.py:3
- backend/venv/Lib/site-packages/django/forms/__init__.py:6
- backend/venv/Lib/site-packages/django/forms/__init__.py:7
- backend/venv/Lib/site-packages/django/forms/__init__.py:8
- backend/venv/Lib/site-packages/django/forms/__init__.py:9
- backend/venv/Lib/site-packages/django/forms/__init__.py:10
- backend/venv/Lib/site-packages/django/forms/__init__.py:11
- backend/venv/Lib/site-packages/h11/_state.py:115
- backend/venv/Lib/site-packages/httpx/__init__.py:2
- backend/venv/Lib/site-packages/httpx/__init__.py:3
- backend/venv/Lib/site-packages/httpx/__init__.py:4
- backend/venv/Lib/site-packages/httpx/__init__.py:5
- backend/venv/Lib/site-packages/httpx/__init__.py:6
- backend/venv/Lib/site-packages/httpx/__init__.py:7
- … et 26 autres

### Classe qui fait tout — Attention ×54

Règle god-class : Une classe avec énormément de méthodes concentre trop de responsabilités : chaque modification risque d'en casser une autre.

Comment corriger : Répartissez ses responsabilités dans des classes plus petites.

- backend/app/communaute/services/espace_service.py:39
- backend/app/communaute/services/publication_service.py:41
- backend/app/devstreet_hub/repositories/workflow_repository.py:25
- backend/app/devstreet_hub/services/gitea_client.py:34
- backend/app/devstreet_hub/services/workflow_service.py:35
- backend/app/marketplace/management/commands/seed_marketplace_demo.py:49
- backend/scripts/generator/code_generator.py:28
- backend/scripts/generator/state_manager.py:38
- backend/venv/Lib/site-packages/PIL/Image.py:617
- backend/venv/Lib/site-packages/PIL/ImageDraw.py:62
- backend/venv/Lib/site-packages/PIL/ImageMath.py:30
- backend/venv/Lib/site-packages/_pytest/assertion/rewrite.py:606
- backend/venv/Lib/site-packages/_pytest/config/__init__.py:460
- backend/venv/Lib/site-packages/_pytest/config/__init__.py:1041
- backend/venv/Lib/site-packages/_pytest/legacypath.py:42
- backend/venv/Lib/site-packages/_pytest/pytester.py:653
- backend/venv/Lib/site-packages/click/core.py:213
- backend/venv/Lib/site-packages/click/core.py:960
- backend/venv/Lib/site-packages/django/contrib/admin/checks.py:177
- backend/venv/Lib/site-packages/django/contrib/admin/options.py:128
- backend/venv/Lib/site-packages/django/contrib/admin/options.py:636
- backend/venv/Lib/site-packages/django/contrib/admin/sites.py:30
- backend/venv/Lib/site-packages/django/contrib/auth/models.py:529
- backend/venv/Lib/site-packages/django/contrib/contenttypes/fields.py:580
- backend/venv/Lib/site-packages/django/db/models/expressions.py:38
- backend/venv/Lib/site-packages/django/db/models/expressions.py:174
- backend/venv/Lib/site-packages/django/db/models/fields/__init__.py:119
- backend/venv/Lib/site-packages/django/db/models/fields/related.py:953
- backend/venv/Lib/site-packages/django/db/models/fields/related.py:1360
- backend/venv/Lib/site-packages/django/db/models/fields/related_descriptors.py:1020
- … et 24 autres

### Action GitHub non épinglée — Attention ×39

Règle workflow-unpinned-action : uses: owner/repo@v1 suit une étiquette modifiable : si l'action est compromise, votre pipeline exécute le nouveau code avec vos secrets.

Comment corriger : Épinglez l'action sur le SHA complet d'un commit.

- .github/workflows/cd-build-images.yml:47
- .github/workflows/cd-build-images.yml:86
- .github/workflows/cd-deploiement-gcp.yml:50
- .github/workflows/cd-deploiement-ssh.yml:51
- .github/workflows/cd-gitea-ssh.yml:37
- .github/workflows/cd-gitea-ssh.yml:110
- .github/workflows/cd-maintenance.yml:50
- .github/workflows/cd-maintenance.yml:153
- .github/workflows/cd-maintenance.yml:242
- .github/workflows/cd-maintenance.yml:382
- .github/workflows/cd-maintenance.yml:503
- .github/workflows/cd-maintenance.yml:582
- .github/workflows/cd-maintenance.yml:676
- .github/workflows/cd-minio-ssh.yml:44
- .github/workflows/cd-minio-ssh.yml:138
- .github/workflows/cd-observabilite-ssh.yml:46
- .github/workflows/cd-observabilite-ssh.yml:140
- .github/workflows/cd-orchestrateur.yml:44
- .github/workflows/cd-orchestrateur.yml:213
- .github/workflows/cd-orchestrateur.yml:259
- .github/workflows/cd-verifier-environnement.yml:48
- .github/workflows/ci-backend.yml:42
- .github/workflows/ci-backend.yml:47
- .github/workflows/ci-frontend.yml:25
- .github/workflows/ci-frontend.yml:30
- .github/workflows/ci-non-regression.yml:59
- .github/workflows/ci-non-regression.yml:67
- .github/workflows/ci-non-regression.yml:74
- .github/workflows/ci-non-regression.yml:142
- .github/workflows/ci-non-regression.yml:185
- … et 9 autres

### Imports circulaires — Attention ×20

Règle import-cycle : Des fichiers s'importent mutuellement en boucle : ordre de chargement fragile, valeurs parfois undefined, code difficile à séparer.

Comment corriger : Déplacez la partie commune dans un module à part que les deux importent.

- backend/scripts/regression_guard/audit.py:6
- backend/venv/Lib/site-packages/click/__init__.py:10
- backend/venv/Lib/site-packages/click/_compat.py:518
- backend/venv/Lib/site-packages/colorama/__init__.py:2
- backend/venv/Lib/site-packages/cyclonedx/output/__init__.py:35
- backend/venv/Lib/site-packages/cyclonedx/validation/__init__.py:26
- backend/venv/Lib/site-packages/django/tasks/__init__.py:4
- backend/venv/Lib/site-packages/django/template/base.py:148
- backend/venv/Lib/site-packages/h11/_events.py:14
- backend/venv/Lib/site-packages/httpcore/_async/connection_pool.py:131
- backend/venv/Lib/site-packages/httpcore/_sync/connection_pool.py:131
- backend/venv/Lib/site-packages/httpcore2/_async/connection_pool.py:123
- backend/venv/Lib/site-packages/httpcore2/_sync/connection_pool.py:123
- backend/venv/Lib/site-packages/httpx/_auth.py:11
- backend/venv/Lib/site-packages/jinja2/__init__.py:6
- backend/venv/Lib/site-packages/markdown_it/__init__.py:6
- backend/venv/Lib/site-packages/openai/__init__.py:9
- backend/venv/Lib/site-packages/packaging/ranges.py:55
- backend/venv/Lib/site-packages/pip/_internal/resolution/resolvelib/candidates.py:30
- backend/venv/Lib/site-packages/pip/_vendor/idna/__init__.py:1

### Appel réseau ou base de données dans une boucle — Attention ×9

Règle io-in-loop : Chaque tour de boucle attend sa réponse : 100 éléments font 100 allers-retours (problème N+1).

Comment corriger : Regroupez les appels en une seule requête, ou lancez-les en parallèle (Promise.all).

- backend/venv/Lib/site-packages/django/contrib/gis/db/backends/oracle/schema.py:98
- backend/venv/Lib/site-packages/django/contrib/gis/db/backends/spatialite/schema.py:88
- backend/venv/Lib/site-packages/django/contrib/gis/db/backends/spatialite/schema.py:102
- backend/venv/Lib/site-packages/django/contrib/gis/db/backends/spatialite/schema.py:120
- backend/venv/Lib/site-packages/django/contrib/gis/db/backends/spatialite/schema.py:149
- backend/venv/Lib/site-packages/django/contrib/gis/db/backends/spatialite/schema.py:161
- backend/venv/Lib/site-packages/django/contrib/gis/db/backends/spatialite/schema.py:174
- backend/venv/Lib/site-packages/django/contrib/gis/db/backends/spatialite/schema.py:185
- backend/venv/Lib/site-packages/django/db/models/sql/compiler.py:1925

### Égalité exacte entre nombres décimaux — Attention ×7

Règle float-equality : Les nombres à virgule sont arrondis en binaire : 0,1 + 0,2 ne vaut pas exactement 0,3. Une comparaison exacte échoue au hasard.

Comment corriger : Comparez avec une tolérance : abs(a - b) < epsilon.

- backend/venv/Lib/site-packages/_pytest/python_api.py:180
- backend/venv/Lib/site-packages/_pytest/python_api.py:272
- backend/venv/Lib/site-packages/_pytest/python_api.py:356
- backend/venv/Lib/site-packages/charset_normalizer/api.py:665
- backend/venv/Lib/site-packages/django/contrib/gis/db/models/fields.py:316
- backend/venv/Lib/site-packages/django/contrib/gis/db/models/functions.py:578
- backend/venv/Lib/site-packages/gunicorn/util.py:353

### Test désactivé — Attention ×5

Règle no-skipped-tests : Un test ignoré (.skip, xit, skip) donne une fausse impression de couverture.

Comment corriger : Réparez le test ou supprimez-le.

- backend/venv/Lib/site-packages/colorama/tests/initialise_test.py:20
- backend/venv/Lib/site-packages/colorama/tests/winterm_test.py:25
- backend/venv/Lib/site-packages/colorama/tests/winterm_test.py:66
- backend/venv/Lib/site-packages/colorama/tests/winterm_test.py:77
- backend/venv/Lib/site-packages/colorama/tests/winterm_test.py:88

### Recherche répétée dans une boucle — Attention ×5

Règle quadratic-loop : Chercher dans une liste à chaque tour de boucle fait un travail qui grandit au carré : lent dès qu'il y a beaucoup de données.

Comment corriger : Construisez une Map ou un Set avant la boucle pour chercher instantanément.

- backend/venv/Lib/site-packages/django/contrib/admin/static/admin/js/SelectBox.js:36
- backend/venv/Lib/site-packages/django/contrib/admin/static/admin/js/change_form.js:10
- backend/venv/Lib/site-packages/django/contrib/admin/static/admin/js/nav_sidebar.js:49
- backend/venv/Lib/site-packages/drf_yasg/static/drf-yasg/swagger-ui-dist/swagger-ui-es-bundle-core.js:2
- backend/venv/Lib/site-packages/drf_yasg/static/drf-yasg/swagger-ui-dist/swagger-ui-es-bundle-core.js:2

### Code jamais exécuté — Attention ×5

Règle unreachable-code : Ce code suit un return, un throw ou un break : il ne s'exécute jamais et trompe la personne qui lit.

Comment corriger : Supprimez-le.

- backend/venv/Lib/site-packages/drf_yasg/static/drf-yasg/swagger-ui-dist/swagger-ui-es-bundle-core.js:2
- backend/venv/Lib/site-packages/httpx/_content.py:104
- backend/venv/Lib/site-packages/httpx/_types.py:97
- backend/venv/Lib/site-packages/httpx/_types.py:111
- backend/venv/Lib/site-packages/httpx2/_content.py:105

### alert(), confirm() ou prompt() — Attention ×2

Règle no_alert : Ces boîtes de dialogue bloquent la page et gênent l'utilisateur. Ce sont souvent des restes de débogage.

Comment corriger : Utilisez une fenêtre ou un message intégré à l'interface.

- backend/venv/Lib/site-packages/django/contrib/admin/static/admin/js/actions.js:161
- backend/venv/Lib/site-packages/django/contrib/admin/static/admin/js/actions.js:176

### Affectation dans une condition — Attention ×1

Règle assignment-in-condition : if (x = y) affecte au lieu de comparer : c'est presque toujours un == oublié, et la condition devient toujours vraie ou toujours fausse.

Comment corriger : Corrigez la comparaison, ou sortez l'affectation de la condition.

- backend/venv/Lib/site-packages/drf_yasg/static/drf-yasg/swagger-ui-dist/swagger-ui-es-bundle-core.js:2

### Import des fichiers internes d'un module — Attention ×1

Règle deep-import-internals : Importer /internal/, /src/ ou /dist/ d'un autre module contourne son interface publique et casse à sa prochaine réorganisation.

Comment corriger : Importez depuis le point d'entrée public du module.

- backend/venv/Lib/site-packages/drf_yasg/static/drf-yasg/swagger-ui-dist/swagger-ui-es-bundle-core.js:2

### Comparaison avec == au lieu de === — Attention ×1

Règle loose-equality : == convertit les types avant de comparer : 0 == '' est vrai, ce qui cause des bugs discrets.

Comment corriger : Utilisez === et !==.

- backend/venv/Lib/site-packages/drf_yasg/static/drf-yasg/swagger-ui-dist/swagger-ui-es-bundle-core.js:2

### return dans un bloc finally — Attention ×1

Règle return-in-finally : Un return, throw ou break dans finally remplace le résultat ou l'erreur du try : une exception disparaît sans bruit.

Comment corriger : Sortez ce return du bloc finally.

- backend/venv/Lib/site-packages/drf_yasg/static/drf-yasg/swagger-ui-dist/swagger-ui-es-bundle-core.js:2

### Copie de l'accumulateur dans reduce — Attention ×1

Règle spread-in-reducer : {...acc} recopie tout l'accumulateur à chaque tour : le traitement devient très lent sur une grande liste.

Comment corriger : Modifiez l'accumulateur directement (acc[k] = v, push), ou utilisez une boucle.

- backend/venv/Lib/site-packages/drf_yasg/static/drf-yasg/swagger-ui-dist/swagger-ui-es-bundle-core.js:2

### Promesse sans gestion d'erreur — Attention ×1

Règle unhandled-promise : Un .then() sans .catch() : si la promesse échoue, l'erreur n'est capturée nulle part et peut arrêter le processus Node.

Comment corriger : Ajoutez un .catch(), ou utilisez await dans un try/catch.

- backend/venv/Lib/site-packages/drf_yasg/static/drf-yasg/swagger-ui-dist/swagger-ui-es-bundle-core.js:2

### Nom de branche hors convention — Attention ×1

Règle branch-naming : Un nom de branche sans préfixe ne dit pas ce qu'elle contient.

Comment corriger : Utilisez un préfixe : feature/, fix/, hotfix/ ou release/.

- Historique Git:1

### Message de commit hors convention — Attention ×1

Règle conventional-commit : Sans préfixe (feat:, fix:, docs:…), l'historique est difficile à parcourir et on ne peut pas générer de journal des modifications.

Comment corriger : Commencez vos messages par feat:, fix:, chore:, docs:, refactor: ou test:.

- Historique Git:1

### Conditions ternaires imbriquées — Info ×151

Règle nested-ternary : Plusieurs ? : enchaînés sont très difficiles à lire.

Comment corriger : Remplacez-les par un if/else ou une petite fonction.

- backend/venv/Lib/site-packages/drf_yasg/static/drf-yasg/immutable.js:9
- backend/venv/Lib/site-packages/drf_yasg/static/drf-yasg/immutable.js:165
- backend/venv/Lib/site-packages/drf_yasg/static/drf-yasg/immutable.js:167
- backend/venv/Lib/site-packages/drf_yasg/static/drf-yasg/immutable.js:207
- backend/venv/Lib/site-packages/drf_yasg/static/drf-yasg/immutable.js:247
- backend/venv/Lib/site-packages/drf_yasg/static/drf-yasg/immutable.js:287
- backend/venv/Lib/site-packages/drf_yasg/static/drf-yasg/immutable.js:302
- backend/venv/Lib/site-packages/drf_yasg/static/drf-yasg/immutable.js:303
- backend/venv/Lib/site-packages/drf_yasg/static/drf-yasg/immutable.js:332
- backend/venv/Lib/site-packages/drf_yasg/static/drf-yasg/immutable.js:333
- backend/venv/Lib/site-packages/drf_yasg/static/drf-yasg/immutable.js:548
- backend/venv/Lib/site-packages/drf_yasg/static/drf-yasg/immutable.js:549
- backend/venv/Lib/site-packages/drf_yasg/static/drf-yasg/immutable.js:550
- backend/venv/Lib/site-packages/drf_yasg/static/drf-yasg/immutable.js:585
- backend/venv/Lib/site-packages/drf_yasg/static/drf-yasg/immutable.js:586
- backend/venv/Lib/site-packages/drf_yasg/static/drf-yasg/immutable.js:779
- backend/venv/Lib/site-packages/drf_yasg/static/drf-yasg/immutable.js:1217
- backend/venv/Lib/site-packages/drf_yasg/static/drf-yasg/immutable.js:1927
- backend/venv/Lib/site-packages/drf_yasg/static/drf-yasg/immutable.js:1986
- backend/venv/Lib/site-packages/drf_yasg/static/drf-yasg/immutable.js:2100
- backend/venv/Lib/site-packages/drf_yasg/static/drf-yasg/immutable.js:2101
- backend/venv/Lib/site-packages/drf_yasg/static/drf-yasg/immutable.js:2507
- backend/venv/Lib/site-packages/drf_yasg/static/drf-yasg/immutable.js:2545
- backend/venv/Lib/site-packages/drf_yasg/static/drf-yasg/immutable.js:2646
- backend/venv/Lib/site-packages/drf_yasg/static/drf-yasg/immutable.js:3484
- backend/venv/Lib/site-packages/drf_yasg/static/drf-yasg/immutable.js:3585
- backend/venv/Lib/site-packages/drf_yasg/static/drf-yasg/immutable.js:3593
- backend/venv/Lib/site-packages/drf_yasg/static/drf-yasg/immutable.js:3611
- backend/venv/Lib/site-packages/drf_yasg/static/drf-yasg/immutable.js:3794
- backend/venv/Lib/site-packages/drf_yasg/static/drf-yasg/immutable.js:3952
- … et 121 autres

### else inutile après un return — Info ×21

Règle else-after-return : Le if se termine déjà par un return : le else ajoute un niveau d'indentation pour rien.

Comment corriger : Supprimez le else et désindentez son contenu.

- backend/venv/Lib/site-packages/django/contrib/admin/static/admin/js/admin/DateTimeShortcuts.js:51
- backend/venv/Lib/site-packages/drf_yasg/static/drf-yasg/immutable.js:1126
- backend/venv/Lib/site-packages/drf_yasg/static/drf-yasg/immutable.js:1128
- backend/venv/Lib/site-packages/drf_yasg/static/drf-yasg/immutable.js:1130
- backend/venv/Lib/site-packages/drf_yasg/static/drf-yasg/immutable.js:1137
- backend/venv/Lib/site-packages/drf_yasg/static/drf-yasg/immutable.js:1762
- backend/venv/Lib/site-packages/drf_yasg/static/drf-yasg/immutable.js:1766
- backend/venv/Lib/site-packages/drf_yasg/static/drf-yasg/immutable.js:1820
- backend/venv/Lib/site-packages/drf_yasg/static/drf-yasg/immutable.js:2757
- backend/venv/Lib/site-packages/drf_yasg/static/drf-yasg/immutable.js:2761
- backend/venv/Lib/site-packages/drf_yasg/static/drf-yasg/immutable.js:2772
- backend/venv/Lib/site-packages/drf_yasg/static/drf-yasg/immutable.js:3231
- backend/venv/Lib/site-packages/drf_yasg/static/drf-yasg/immutable.js:3233
- backend/venv/Lib/site-packages/drf_yasg/static/drf-yasg/immutable.js:3313
- backend/venv/Lib/site-packages/drf_yasg/static/drf-yasg/immutable.js:3314
- backend/venv/Lib/site-packages/drf_yasg/static/drf-yasg/immutable.js:3316
- backend/venv/Lib/site-packages/drf_yasg/static/drf-yasg/immutable.js:3494
- backend/venv/Lib/site-packages/drf_yasg/static/drf-yasg/immutable.js:3601
- backend/venv/Lib/site-packages/drf_yasg/static/drf-yasg/insQ.js:83
- backend/venv/Lib/site-packages/drf_yasg/static/drf-yasg/insQ.js:131
- backend/venv/Lib/site-packages/drf_yasg/static/drf-yasg/swagger-ui-dist/swagger-ui-es-bundle-core.js:2

### Couches mélangées — Info ×15

Règle mvc : Accès aux données ou affichage se trouvent dans la logique applicative : chaque changement touche plusieurs couches à la fois.

Comment corriger : Isolez l'accès aux données (modèle) et l'affichage (vue) hors du contrôleur.

- backend/scripts/security_scan/rules/python_rules.py:52
- backend/scripts/security_scan/rules/python_rules.py:53
- backend/venv/Lib/site-packages/django/contrib/admin/static/admin/js/SelectBox.js:17
- backend/venv/Lib/site-packages/django/contrib/admin/static/admin/js/inlines.js:53
- backend/venv/Lib/site-packages/django/contrib/admin/static/admin/js/inlines.js:57
- backend/venv/Lib/site-packages/django/contrib/admin/static/admin/js/inlines.js:107
- backend/venv/Lib/site-packages/django/contrib/admin/static/admin/js/inlines.js:111
- backend/venv/Lib/site-packages/django/contrib/admin/static/admin/js/inlines.js:115
- backend/venv/Lib/site-packages/django/contrib/gis/db/backends/oracle/schema.py:7
- backend/venv/Lib/site-packages/django/contrib/gis/db/backends/oracle/schema.py:24
- backend/venv/Lib/site-packages/django/contrib/gis/db/backends/oracle/schema.py:27
- backend/venv/Lib/site-packages/django/contrib/gis/db/backends/postgis/base.py:116
- backend/venv/Lib/site-packages/django/db/models/sql/datastructures.py:180
- backend/venv/Lib/site-packages/drf_yasg/openapi.py:120
- backend/venv/Lib/site-packages/drf_yasg/static/drf-yasg/insQ.js:45

### Dépendance pas à jour — Info ×8

Règle outdated-dependency : Une version plus récente du paquet existe. Les vieilles versions accumulent les bugs connus et rendent les futures mises à jour plus difficiles.

Comment corriger : Mettez à jour vers la version indiquée et relancez vos tests.

- backend/requirements.txt
- backend/requirements.txt
- backend/requirements.txt
- backend/requirements.txt
- backend/requirements.txt
- backend/requirements.txt
- backend/requirements.txt
- backend/requirements.txt

### SELECT * dans une requête — Info ×8

Règle sql-select-star : Récupérer toutes les colonnes charge des données inutiles et casse le code si une colonne est ajoutée.

Comment corriger : Listez les colonnes nécessaires.

- backend/scripts/security_scan/rules/python_rules.py:52
- backend/scripts/security_scan/rules/python_rules.py:53
- backend/venv/Lib/site-packages/django/contrib/gis/db/backends/postgis/introspection.py:45
- backend/venv/Lib/site-packages/django/db/models/sql/compiler.py:648
- backend/venv/Lib/site-packages/django/db/models/sql/compiler.py:724
- backend/venv/Lib/site-packages/django/db/models/sql/compiler.py:932
- backend/venv/Lib/site-packages/django/db/models/sql/compiler.py:2017
- backend/venv/Lib/site-packages/django/db/models/sql/datastructures.py:180

### Attente fixe codée en dur — Info ×7

Règle magic-sleep : Attendre une durée fixe (sleep) en espérant qu'une ressource soit prête est fragile : trop court, ça échoue ; trop long, ça ralentit.

Comment corriger : Attendez un vrai signal : événement, réponse, ou nouvel essai avec un délai croissant.

- backend/scripts/smoke_git_computer_auth.py:178
- backend/scripts/smoke_git_computer_auth.py:188
- backend/scripts/smoke_git_computer_auth.py:242
- backend/venv/Lib/site-packages/click/_winconsole.py:149
- backend/venv/Lib/site-packages/gunicorn/sock.py:217
- backend/venv/Lib/site-packages/gunicorn/workers/base.py:129
- backend/venv/Lib/site-packages/gunicorn/workers/base.py:193

### Accès en cascade à d'autres objets — Info ×6

Règle feature-envy : Une chaîne comme a.b.c.d.e montre que ce code dépend de la structure interne d'autres objets.

Comment corriger : Déplacez cette logique dans l'objet qui possède les données, ou ajoutez-lui une méthode dédiée.

- backend/venv/Lib/site-packages/django/contrib/admin/static/admin/js/nav_sidebar.js:56
- backend/venv/Lib/site-packages/django/contrib/admin/static/admin/js/nav_sidebar.js:56
- backend/venv/Lib/site-packages/django/contrib/gis/static/gis/js/OLMapWidget.js:28
- backend/venv/Lib/site-packages/django/contrib/gis/static/gis/js/OLMapWidget.js:28
- backend/venv/Lib/site-packages/drf_yasg/static/drf-yasg/immutable.js:1144
- backend/venv/Lib/site-packages/drf_yasg/static/drf-yasg/swagger-ui-dist/swagger-ui-es-bundle-core.js:2

### !important dans le CSS — Info ×4

Règle css-important-overuse : !important force un style et oblige le suivant à en rajouter un : la feuille de style devient impossible à maîtriser.

Comment corriger : Augmentez plutôt la précision du sélecteur, ou réorganisez les règles.

- backend/venv/Lib/site-packages/django/contrib/admin/static/admin/css/base.css:321
- backend/venv/Lib/site-packages/django/contrib/admin/static/admin/css/responsive.css:797
- backend/venv/Lib/site-packages/django/contrib/admin/static/admin/css/responsive.css:798
- backend/venv/Lib/site-packages/django/contrib/admin/static/admin/css/responsive.css:799

### Langue de la page non précisée — Info ×2

Règle missing-html-lang : Sans lang sur <html>, les lecteurs d'écran prononcent mal le texte et les moteurs de recherche devinent la langue.

Comment corriger : Ajoutez lang="fr" (ou la langue de la page) sur la balise <html>.

- .agents/skills/illustre/references/render_template.html:2
- backend/venv/Lib/site-packages/django/contrib/admin/templates/admin/popup_response.html:2

### Nombre sans explication — Info ×2

Règle magic-number : Un nombre écrit tel quel dans une comparaison ne dit pas ce qu'il représente (un délai, une limite, un code).

Comment corriger : Mettez-le dans une constante au nom explicite.

- backend/venv/Lib/site-packages/drf_yasg/static/drf-yasg/immutable.js:139
- backend/venv/Lib/site-packages/drf_yasg/static/drf-yasg/swagger-ui-dist/swagger-ui-es-bundle-core.js:2

### Pas de contrôle de santé du conteneur — Info ×1

Règle dockerfile-missing-healthcheck : Sans HEALTHCHECK, l'orchestrateur ne voit pas qu'un conteneur est bloqué et ne le redémarre pas.

Comment corriger : Ajoutez une instruction HEALTHCHECK qui interroge l'application.

- backend/Dockerfile:1

### Fichier jamais importé — Info ×1

Règle orphan-module : Aucun autre fichier n'importe ce module : il n'est probablement plus utilisé.

Comment corriger : Vérifiez qu'il ne sert plus, puis supprimez-le.

- backend/venv/Lib/site-packages/drf_yasg/static/drf-yasg/swagger-ui-dist/swagger-ui-es-bundle-core.js:2

### Export jamais utilisé — Info ×1

Règle unused-export : Cet élément est exporté mais aucun autre fichier ne l'importe : c'est probablement du code mort.

Comment corriger : Supprimez l'export, ou l'élément entier s'il ne sert plus.

- backend/venv/Lib/site-packages/drf_yasg/static/drf-yasg/swagger-ui-dist/swagger-ui-es-bundle-core.js:2

### Titre de commit trop long — Info ×1

Règle commit-too-long : Au-delà de 72 caractères, le titre est coupé dans la plupart des outils.

Comment corriger : Résumez en une ligne courte et mettez le détail dans le corps du message.

- Historique Git:1

### Requête SQL construite par formatage — À revoir ×17

Règle sql-string-format : La requête SQL est fabriquée en collant une valeur dans le texte (format!, f-string, Sprintf). Si cette valeur vient d'un utilisateur, il peut y glisser du SQL et lire, modifier ou effacer la base.

Comment corriger : Gardez la requête fixe et passez la valeur en paramètre lié : $1 ou ? dans le SQL, puis .bind(valeur).

Règle peu fiable sur le corpus de mesure : à vérifier, hors note.

- backend/scripts/create_app_template.py:111
- backend/scripts/create_app_template.py:178
- backend/scripts/create_app_template.py:225
- backend/scripts/create_app_template.py:275
- backend/scripts/generator/code_generator.py:750
- backend/scripts/generator/frontend_generator.py:504
- backend/scripts/generator/frontend_generator.py:516
- backend/scripts/generator/frontend_generator.py:537
- backend/scripts/security_scan/rules/python_rules.py:52
- backend/venv/Lib/site-packages/django/contrib/admin/options.py:990
- backend/venv/Lib/site-packages/django/db/models/functions/text.py:273
- backend/venv/Lib/site-packages/django/db/models/query.py:1287
- backend/venv/Lib/site-packages/django/db/models/sql/compiler.py:648
- backend/venv/Lib/site-packages/django/db/models/sql/query.py:2578
- backend/venv/Lib/site-packages/jinja2/compiler.py:825
- backend/venv/Lib/site-packages/jinja2/compiler.py:1171
- backend/venv/Lib/site-packages/pip/_internal/self_outdated_check.py:150

### Fichier .env versionné — À revoir ×1

Règle committed-env-file : Le fichier .env contient en général les mots de passe et clés de l'application. Le versionner les expose à toute personne qui a accès au dépôt.

Comment corriger : Retirez-le du dépôt (git rm --cached .env), ajoutez-le au .gitignore et changez les secrets qu'il contenait.

Règle peu fiable sur le corpus de mesure : à vérifier, hors note.

- backend/.env:1

### Fichier de clé privée versionné — À revoir ×1

Règle private-key-block : Une clé privée est enregistrée dans un fichier du dépôt. Elle reste dans l'historique Git même après suppression du fichier.

Comment corriger : Retirez le fichier, ajoutez-le au .gitignore et remplacez la clé, qui doit être considérée comme compromise.

Règle peu fiable sur le corpus de mesure : à vérifier, hors note.

- backend/scripts/security_scan/rules/secret_rules.py:12

### Adresse en HTTP non chiffré — À revoir ×39

Règle insecure_transport : Les échanges en http:// circulent en clair : toute personne sur le réseau peut les lire ou les modifier.

Comment corriger : Utilisez https://.

Règle peu fiable sur le corpus de mesure : à vérifier, hors note.

- backend/scripts/deploy_env/spec.py:115
- backend/venv/Lib/site-packages/PIL/DdsImagePlugin.py:1
- backend/venv/Lib/site-packages/PIL/JpegImagePlugin.py:119
- backend/venv/Lib/site-packages/PIL/JpegImagePlugin.py:786
- backend/venv/Lib/site-packages/PIL/JpegPresets.py:1
- backend/venv/Lib/site-packages/_pytest/assertion/rewrite.py:607
- backend/venv/Lib/site-packages/cachecontrol/heuristics.py:29
- backend/venv/Lib/site-packages/cachecontrol/heuristics.py:98
- backend/venv/Lib/site-packages/colorama/ansi.py:2
- backend/venv/Lib/site-packages/cyclonedx/model/__init__.py:680
- backend/venv/Lib/site-packages/cyclonedx/output/json.py:107
- backend/venv/Lib/site-packages/cyclonedx/output/json.py:113
- backend/venv/Lib/site-packages/cyclonedx/output/json.py:119
- backend/venv/Lib/site-packages/cyclonedx/output/json.py:125
- backend/venv/Lib/site-packages/cyclonedx/output/json.py:131
- backend/venv/Lib/site-packages/cyclonedx/output/xml.py:94
- backend/venv/Lib/site-packages/cyclonedx/validation/json.py:95
- backend/venv/Lib/site-packages/django/contrib/gis/feeds.py:94
- backend/venv/Lib/site-packages/django/contrib/gis/feeds.py:109
- backend/venv/Lib/site-packages/django/contrib/gis/serializers/geojson.py:9
- backend/venv/Lib/site-packages/gunicorn/systemd.py:49
- backend/venv/Lib/site-packages/gunicorn/util.py:522
- backend/venv/Lib/site-packages/httpx/_models.py:94
- backend/venv/Lib/site-packages/license_expression/_pyahocorasick.py:7
- backend/venv/Lib/site-packages/markdown_it/common/html_blocks.py:1
- backend/venv/Lib/site-packages/markdown_it/common/utils.py:264
- backend/venv/Lib/site-packages/mccabe.py:1
- backend/venv/Lib/site-packages/packageurl/contrib/purl2url.py:634
- backend/venv/Lib/site-packages/packageurl/contrib/route.py:31
- backend/venv/Lib/site-packages/packageurl/contrib/route.py:148
- … et 9 autres

### Cookie sans protections — À revoir ×5

Règle insecure_cookie : Un cookie sans HttpOnly, Secure ou SameSite peut être lu par un script, envoyé en clair ou utilisé depuis un autre site.

Comment corriger : Ajoutez HttpOnly, Secure et SameSite=Lax (ou Strict) aux cookies de session.

Règle peu fiable sur le corpus de mesure : à vérifier, hors note.

- backend/app/core/cookies.py:23
- backend/app/core/cookies.py:28
- backend/venv/Lib/site-packages/httpx/_models.py:1097
- backend/venv/Lib/site-packages/httpx/_models.py:1141
- backend/venv/Lib/site-packages/httpx/_models.py:1208

### Fichier de secrets versionné — À revoir ×2

Règle committed-secret-file : Un fichier de clés ou d'identifiants (.pem, .p12, credentials…) est dans le dépôt.

Comment corriger : Retirez-le du dépôt, ajoutez-le au .gitignore et révoquez ce qu'il contient.

Règle peu fiable sur le corpus de mesure : à vérifier, hors note.

- backend/venv/Lib/site-packages/certifi/cacert.pem:1
- backend/venv/Lib/site-packages/pip/_vendor/certifi/cacert.pem:1

### Chemin temporaire écrit en dur — À revoir ×1

Règle insecure-temp-path : Un chemin fixe dans /tmp peut être créé d'avance par un autre programme, qui pourrait alors lire ou remplacer vos données.

Comment corriger : Créez un fichier temporaire unique avec l'API du langage (mkstemp, tempfile).

Règle peu fiable sur le corpus de mesure : à vérifier, hors note.

- backend/venv/Lib/site-packages/jinja2/bccache.py:189

## Dépendances vulnérables

- @modelcontextprotocol/sdk 1.17.1 — GHSA-f897-62hf-6gxq (Critique) : MCP TypeScript SDK: HTTP server transports and handlers did not limit request body size or JSON-RPC batch length — corrigé en 1.30.1
- body-parser 2.2.0 — CVE-2026-111181 (Critique) : body-parser vulnerable to Denial of Service via trailing bytes after a compressed request body — corrigé en 2.4.0
- djangorestframework 3.17.2 — CVE-2026-114138 (Critique) : Django REST framework: Accept header with many large quoted parameters burns ~19s of CPU per request in content negotiation — corrigé en 3.18.2
- djangorestframework 3.17.2 — CVE-2026-114136 (Critique) : Django REST framework: JSONParser applies an attacker-named codec to the request stream — corrigé en 3.18.2
- djangorestframework 3.17.2 — CVE-2026-114137 (Critique) : Django REST framework: TokenProxy.delete() reports success and revokes nothing — corrigé en 3.18.2
- black 26.5.1 — CVE-2026-114134 (Critique) : Black: GitHub Action installs unvalidated required-version from pyproject.toml — corrigé en 26.10.1
- @modelcontextprotocol/sdk 1.17.1 — CVE-2026-111768 (Critique) : MCP TypeScript SDK: One HTTP request within the default size limit could exhaust server memory during validation — corrigé en 1.32.0
- vite 7.1.2 — CVE-2026-112942 (Critique) : launch-editor: `fs.existsSync()` existence check can be bypassed on Windows — corrigé en 7.3.7
- @modelcontextprotocol/sdk 1.17.1 — CVE-2026-104850 (Critique) : MCP TypeScript SDK: OAuth client could send credentials to an authorization server chosen by the MCP server — corrigé en 1.31.0
- proxy-addr 2.0.7 — CVE-2026-90711 (Critique) : proxy-addr vulnerable to IP spoofing via IPv4-mapped IPv6 trust subnet — corrigé en 2.0.8
- tinypool 1.1.1 — CVE-2026-104848 (Critique) : Tinypool: Prototype Pollution gadget in worker options leads to Remote Code Execution — corrigé en 2.1.1
- tinypool 1.1.1 — CVE-2026-104849 (Critique) : Tinypool: Prototype Pollution Gadget to RCE in run() options — corrigé en 2.1.2
- zod 3.25.76 — CVE-2023-54404 (Critique) : Zod can exhaust memory while validating oversized constrained collections — corrigé en 4.6.6
- zod 4.0.10 — CVE-2023-54404 (Critique) : Zod can exhaust memory while validating oversized constrained collections — corrigé en 4.6.6
- brace-expansion 2.0.2 — CVE-2026-102276 (Critique) : brace-expansion: DoS via uncontrolled recursion in parseCommaParts causing stack exhaustion — corrigé en 2.1.5
- brace-expansion 2.0.2 — CVE-2026-102278 (Critique) : brace-expansion: DoS via uncontrolled recursion on nested brace groups causing stack exhaustion — corrigé en 2.1.6
- brace-expansion 1.1.12 — CVE-2026-102276 (Critique) : brace-expansion: DoS via uncontrolled recursion in parseCommaParts causing stack exhaustion — corrigé en 1.1.19
- brace-expansion 1.1.12 — CVE-2026-102278 (Critique) : brace-expansion: DoS via uncontrolled recursion on nested brace groups causing stack exhaustion — corrigé en 1.1.20
- js-yaml 4.1.0 — CVE-2026-84375 (Critique) : js-yaml: maxTotalMergeKeys does not limit CPU use for empty merge sources — corrigé en 4.3.2
- browserslist 4.25.1 — CVE-2026-73088 (Critique) : Browserslist: Uncaught crash / prototype write via untrusted browserslist-stats.json custom stats (normalizeStats) — corrigé en 4.28.7
- browserslist 4.25.1 — CVE-2026-73089 (Critique) : Browserslist: Unbounded memory growth (no cache eviction) via distinct query results, leading to eventual OOM — corrigé en 4.28.7
- js-yaml 4.1.0 — GHSA-5p4m-2wfm-xmqj (Critique) : JS-YAML: Quadratic CPU consumption in !!omap resolution (3.x and 4.x) — CVE-2026-59870 fix not backported — corrigé en 4.3.1
- brace-expansion 2.0.2 — CVE-2026-69152 (Critique) : brace-expansion: DoS via unbounded intermediate arrays, bypassing the CVE-2026-14257 mitigation — corrigé en 2.1.4
- brace-expansion 1.1.12 — CVE-2026-69152 (Critique) : brace-expansion: DoS via unbounded intermediate arrays, bypassing the CVE-2026-14257 mitigation — corrigé en 1.1.18
- brace-expansion 2.0.2 — CVE-2026-14257 (Critique) : brace-expansion: DoS via unbounded expansion length causing an out-of-memory process crash — corrigé en 2.1.3
- brace-expansion 1.1.12 — CVE-2026-14257 (Critique) : brace-expansion: DoS via unbounded expansion length causing an out-of-memory process crash — corrigé en 1.1.17
- tar 7.4.3 — CVE-2026-73566 (Critique) : node-tar: Uncontrolled recursion in mapHas/filesFilter allows uncatchable stack-overflow DoS via crafted long-path tar with member selection — corrigé en 7.5.21
- js-yaml 4.1.0 — CVE-2026-59869 (Critique) : js-yaml: YAML merge-key chains can force quadratic CPU consumption — corrigé en 4.3.0
- tar 7.4.3 — CVE-2026-59873 (Critique) : node-tar: Decompression/parse DoS via unlimited input — corrigé en 7.5.19
- tar 7.4.3 — CVE-2026-59874 (Critique) : node-tar: Negative tar entry size causes infinite loop in archive replace — corrigé en 7.5.18
- brace-expansion 2.0.2 — CVE-2026-13149 (Critique) : brace-expansion: DoS via exponential-time expansion of consecutive non-expanding {} groups — corrigé en 2.1.2
- brace-expansion 1.1.12 — CVE-2026-13149 (Critique) : brace-expansion: DoS via exponential-time expansion of consecutive non-expanding {} groups — corrigé en 1.1.16
- python-socketio 5.13.0 — CVE-2026-48804 (Critique) : python-socketio: Binary attachment accumulation can cause denial of service — corrigé en 5.16.2
- python-socketio 5.13.0 — CVE-2026-48804 (Critique) : python-socketio: Binary attachment accumulation can cause denial of service — corrigé en 5.16.2
- vitest 3.2.4 — CVE-2026-47429 (Critique) : When Vitest UI server is listening, arbitrary file can be read and executed — corrigé en 3.2.6
- vite 7.1.2 — CVE-2026-39363 (Critique) : Vite Vulnerable to Arbitrary File Read via Vite Dev Server WebSocket — corrigé en 7.3.2
- vite 7.1.2 — CVE-2026-39364 (Critique) : Vite: `server.fs.deny` bypassed with queries — corrigé en 7.3.2
- lodash 4.17.21 — CVE-2026-4800 (Critique) : lodash vulnerable to Code Injection via `_.template` imports key names — corrigé en 4.18.0
- path-to-regexp 8.2.0 — CVE-2026-4926 (Critique) : path-to-regexp vulnerable to Denial of Service via sequential optional groups — corrigé en 8.4.0
- picomatch 2.3.1 — CVE-2026-33671 (Critique) : Picomatch has a ReDoS vulnerability via extglob quantifiers — corrigé en 2.3.2
- picomatch 4.0.3 — CVE-2026-33671 (Critique) : Picomatch has a ReDoS vulnerability via extglob quantifiers — corrigé en 4.0.4
- flatted 3.3.3 — CVE-2026-33228 (Critique) : Prototype Pollution via parse() in NodeJS flatted — corrigé en 3.4.2
- flatted 3.3.3 — CVE-2026-32141 (Critique) : flatted vulnerable to unbounded recursion DoS in parse() revive phase — corrigé en 3.4.0
- tar 7.4.3 — CVE-2026-31802 (Critique) : node-tar Symlink Path Traversal via Drive-Relative Linkpath — corrigé en 7.5.11
- tar 7.4.3 — CVE-2026-29786 (Critique) : tar has Hardlink Path Traversal via Drive-Relative Linkpath — corrigé en 7.5.10
- minimatch 7.4.6 — CVE-2026-27904 (Critique) : minimatch ReDoS: nested *() extglobs generate catastrophically backtracking regular expressions — corrigé en 7.4.8
- minimatch 7.4.6 — CVE-2026-27903 (Critique) : minimatch has ReDoS: matchOne() combinatorial backtracking via multiple non-adjacent GLOBSTAR segments — corrigé en 7.4.8
- minimatch 9.0.5 — CVE-2026-27904 (Critique) : minimatch ReDoS: nested *() extglobs generate catastrophically backtracking regular expressions — corrigé en 9.0.7
- minimatch 9.0.5 — CVE-2026-27903 (Critique) : minimatch has ReDoS: matchOne() combinatorial backtracking via multiple non-adjacent GLOBSTAR segments — corrigé en 9.0.7
- minimatch 3.1.2 — CVE-2026-27904 (Critique) : minimatch ReDoS: nested *() extglobs generate catastrophically backtracking regular expressions — corrigé en 3.1.4
- minimatch 3.1.2 — CVE-2026-27903 (Critique) : minimatch has ReDoS: matchOne() combinatorial backtracking via multiple non-adjacent GLOBSTAR segments — corrigé en 3.1.3
- rollup 4.45.3 — CVE-2026-27606 (Critique) : Rollup 4 has Arbitrary File Write via Path Traversal — corrigé en 4.59.0
- tar 7.4.3 — CVE-2026-26960 (Critique) : Arbitrary File Read/Write via Hardlink Target Escape Through Symlink Chain in node-tar Extraction — corrigé en 7.5.8
- minimatch 7.4.6 — CVE-2026-26996 (Critique) : minimatch has a ReDoS via repeated wildcards with non-matching literal in pattern — corrigé en 7.4.7
- minimatch 9.0.5 — CVE-2026-26996 (Critique) : minimatch has a ReDoS via repeated wildcards with non-matching literal in pattern — corrigé en 9.0.6
- minimatch 3.1.2 — CVE-2026-26996 (Critique) : minimatch has a ReDoS via repeated wildcards with non-matching literal in pattern — corrigé en 3.1.3
- @modelcontextprotocol/sdk 1.17.1 — CVE-2026-25536 (Critique) : @modelcontextprotocol/sdk has cross-client data leak via shared server/transport instance reuse — corrigé en 1.26.0
- tar 7.4.3 — CVE-2026-24842 (Critique) : node-tar Vulnerable to Arbitrary File Creation/Overwrite via Hardlink Path Traversal — corrigé en 7.5.7
- tar 7.4.3 — CVE-2026-23950 (Critique) : Race Condition in node-tar Path Reservations via Unicode Ligature Collisions on macOS APFS — corrigé en 7.5.4
- tar 7.4.3 — CVE-2026-23745 (Critique) : node-tar is Vulnerable to Arbitrary File Overwrite and Symlink Poisoning via Insufficient Path Sanitization — corrigé en 7.5.3
- @modelcontextprotocol/sdk 1.17.1 — CVE-2026-0621 (Critique) : Anthropic's MCP TypeScript SDK has a ReDoS vulnerability — corrigé en 1.25.2
- @modelcontextprotocol/sdk 1.17.1 — CVE-2025-66414 (Critique) : Model Context Protocol (MCP) TypeScript SDK does not enable DNS rebinding protection by default — corrigé en 1.24.0
- glob 10.4.5 — CVE-2025-64756 (Critique) : glob CLI: Command injection via -c/--cmd executes matches with shell:true — corrigé en 10.5.0
- minimatch 7.4.6 — CVE-2026-118764 (Attention) : minimatch has potential denial of service via globparts amplification — corrigé en 11.0.1
- minimatch 9.0.5 — CVE-2026-118764 (Attention) : minimatch has potential denial of service via globparts amplification — corrigé en 11.0.1
- glob 10.4.5 — CVE-2026-118773 (Attention) : Glob: AbortSignal cancellation bypass allows post-timeout filesystem traversal — corrigé en 14.0.2
- minimatch 10.2.6 — CVE-2026-118764 (Attention) : minimatch has potential denial of service via globparts amplification — corrigé en 11.0.1
- qs 6.14.0 — CVE-2026-110816 (Attention) : qs : qs.stringify with arrayFormat 'comma' throws an uncaught TypeError on array elements carrying a non-callable own toString (DoS) — corrigé en 6.16.1
- @vitest/mocker 3.2.4 — CVE-2026-112949 (Attention) : Vitest: Code injection via unauthenticated manual mock registration — corrigé en 4.1.12
- vite 7.1.2 — CVE-2026-112946 (Attention) : Vite: Files outside `server.fs.allow` could be served when project paths match system paths on non-Windows machine — corrigé en 7.3.7
- @modelcontextprotocol/sdk 1.17.1 — CVE-2026-111771 (Attention) : MCP TypeScript SDK: Server bearer authentication accepted tokens issued for another service — corrigé en 1.32.0
- @modelcontextprotocol/sdk 1.17.1 — CVE-2026-111769 (Attention) : MCP TypeScript client SDK: HTTP client transports and OAuth requests followed cross-origin redirects and re-sent custom headers and request bodies — corrigé en 1.32.0
- vite 7.1.2 — CVE-2026-112943 (Attention) : launch-editor: escapeCmdArgs() omits % escaping on Windows — corrigé en 7.3.7
- vite 7.1.2 — CVE-2026-112944 (Attention) : launch-editor: Editor CLI flag misinterpretation causing arbitrary command execution for some editors — corrigé en 7.3.7
- postcss-selector-parser 6.1.2 — CVE-2026-104844 (Attention) : PostCSS: Quadratic complexity in flat selector parsing allows CPU exhaustion — corrigé en 6.1.5
- brace-expansion 2.0.2 — CVE-2026-102277 (Attention) : brace-expansion: Quadratic-time expansion of the `{a},b}` rewrite causes CPU denial of service — corrigé en 2.1.7
- brace-expansion 1.1.12 — CVE-2026-102277 (Attention) : brace-expansion: Quadratic-time expansion of the `{a},b}` rewrite causes CPU denial of service — corrigé en 1.1.21
- @vitest/mocker 3.2.4 — CVE-2026-84373 (Attention) : Vitest: Path Traversal / Arbitrary File Read via @vitest/mocker Redirect Mock — corrigé en 4.1.11
- vitest 3.2.4 — CVE-2026-84373 (Attention) : Vitest: Path Traversal / Arbitrary File Read via @vitest/mocker Redirect Mock — corrigé en 4.1.11
- qs 6.14.0 — CVE-2026-82417 (Attention) : qs: Denial of Service via Attacker Controlled isBuffer — corrigé en 6.16.0
- @humanfs/node 0.16.6 — GHSA-p498-v437-472g (Attention) : humanfs: Recursive copy follows symlinked files and copies data from outside the source tree — corrigé en 0.16.8
- tar 7.4.3 — CVE-2026-59875 (Attention) : node-tar: Uncaught Exception DoS via NUL byte in PAX path/linkpath records — corrigé en 7.5.17
- tar 7.4.3 — CVE-2026-59871 (Attention) : node-tar: Process crash via PAX numeric path type confusion — corrigé en 7.5.18
- python-socketio 5.13.0 — CVE-2025-61765 (Attention) : python-socketio vulnerable to arbitrary Python code execution (RCE) through malicious pickle deserialization in certain multi-server deployments — corrigé en 5.14.0
- js-yaml 4.1.0 — CVE-2026-53550 (Attention) : JS-YAML: Quadratic-complexity DoS in merge key handling via repeated aliases — corrigé en 4.2.0
- tar 7.4.3 — CVE-2026-53655 (Attention) : node-tar applies PAX size override to intermediary GNU long-name/long-link headers, causing tar parser interpretation differential (file smuggling) — corrigé en 7.5.16
- vite 7.1.2 — CVE-2026-53571 (Attention) : vite: `server.fs.deny` bypass on Windows alternate paths — corrigé en 7.3.5
- vite 7.1.2 — CVE-2026-53632 (Attention) : launch-editor: NTLMv2 hash disclosure via UNC path handling on Windows — corrigé en 7.3.5
- qs 6.14.0 — CVE-2026-8723 (Attention) : qs has a remotely triggerable DoS: qs.stringify crashes with TypeError on null/undefined entries in comma-format arrays when encodeValuesOnly is set — corrigé en 6.15.2
- vite 7.1.2 — CVE-2026-39365 (Attention) : Vite Vulnerable to Path Traversal in Optimized Deps `.map` Handling — corrigé en 7.3.2
- path-to-regexp 8.2.0 — CVE-2026-4923 (Attention) : path-to-regexp vulnerable to Regular Expression Denial of Service via multiple wildcards — corrigé en 8.4.0
- brace-expansion 2.0.2 — CVE-2026-33750 (Attention) : brace-expansion: Zero-step sequence causes process hang and memory exhaustion — corrigé en 2.0.3
- brace-expansion 1.1.12 — CVE-2026-33750 (Attention) : brace-expansion: Zero-step sequence causes process hang and memory exhaustion — corrigé en 1.1.13
- picomatch 2.3.1 — CVE-2026-33672 (Attention) : Picomatch: Method Injection in POSIX Character Classes causes incorrect Glob Matching — corrigé en 2.3.2
- picomatch 4.0.3 — CVE-2026-33672 (Attention) : Picomatch: Method Injection in POSIX Character Classes causes incorrect Glob Matching — corrigé en 4.0.4
- yaml 2.8.0 — CVE-2026-33532 (Attention) : yaml is vulnerable to Stack Overflow via deeply nested YAML collections — corrigé en 2.8.3
- ajv 6.12.6 — CVE-2025-69873 (Attention) : ajv has ReDoS when using `$data` option — corrigé en 6.14.0
- lodash 4.17.21 — CVE-2025-13465 (Attention) : Lodash has Prototype Pollution Vulnerability in `_.unset`, `_.omit`, and `_.pullAt` functions — corrigé en 4.17.23
- qs 6.14.0 — CVE-2025-15284 (Attention) : qs's arrayLimit bypass in its bracket notation allows DoS via memory exhaustion — corrigé en 6.14.1
- body-parser 2.2.0 — CVE-2025-13466 (Attention) : body-parser is vulnerable to denial of service when url encoding is used — corrigé en 2.2.1
- js-yaml 4.1.0 — CVE-2025-64718 (Attention) : js-yaml has prototype pollution in merge (<<) — corrigé en 4.1.1
- vite 7.1.2 — CVE-2025-62522 (Attention) : vite allows server.fs.deny bypass via backslash on Windows — corrigé en 7.1.11
- python-socketio 5.13.0 — CVE-2025-61765 (Attention) : python-socketio vulnerable to arbitrary Python code execution (RCE) through malicious pickle deserialization in certain multi-server deployments — corrigé en 5.14.0
- vite 7.1.2 — CVE-2026-112945 (Info) : Vite: Cross origin script execution through Vite custom middleware — corrigé en 7.3.7
- deepmerge 4.3.1 — CVE-2026-93753 (Info) : deepmerge mergeObject() allows prototype poisoning of returned objects — pas encore de correctif
- body-parser 2.2.0 — CVE-2026-12590 (Info) : body-parser vulnerable to denial of service when invalid limit value silently disables size enforcement — corrigé en 2.3.0
- @babel/core 7.28.0 — CVE-2026-49356 (Info) : @babel/core: Arbitrary File Read via sourceMappingURL Comment — corrigé en 7.29.6
- postcss-selector-parser 6.1.2 — CVE-2026-9358 (Info) : postcss-selector-parser allows denial of service through uncontrolled AST recursion — corrigé en 6.1.3
- qs 6.14.0 — CVE-2026-2391 (Info) : qs's arrayLimit bypass in comma parsing allows denial of service — corrigé en 6.14.2
- diff 5.2.0 — CVE-2026-24001 (Info) : jsdiff has a Denial of Service vulnerability in parsePatch and applyPatch — corrigé en 5.2.2
- vite 7.1.2 — CVE-2025-58751 (Info) : Vite middleware may serve files starting with the same name with the public directory — corrigé en 7.1.5
- vite 7.1.2 — CVE-2025-58752 (Info) : Vite's `server.fs` settings were not applied to HTML files — corrigé en 7.1.5
