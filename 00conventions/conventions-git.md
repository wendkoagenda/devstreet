# 🔧 Conventions Git & Commandes Utiles

## 📝 Conventions de Commits

### Format Standard

```
<type>(<scope>): <description>

[body optionnel]

[footer optionnel]
```

### Types de Commits

- **feat**: Nouvelle fonctionnalité
- **fix**: Correction de bug
- **docs**: Documentation uniquement
- **style**: Changements qui n'affectent pas le sens du code (espaces, formatage, etc.)
- **refactor**: Changement de code qui ne corrige pas un bug ni n'ajoute une fonctionnalité
- **perf**: Changement de code qui améliore les performances
- **test**: Ajout de tests manquants ou correction de tests existants
- **chore**: Changements aux outils de build ou aux dépendances
- **ci**: Changements aux fichiers et scripts de CI
- **revert**: Annulation d'un commit précédent

### Exemples de Commits

````bash
# Nouvelle fonctionnalité
feat(auth): ajouter la fonctionnalité de connexion utilisateur

# Correction de bug
fix(api): résoudre l'exception de pointeur nul dans le service utilisateur

# Documentation
docs(readme): mettre à jour les instructions d'installation

# Refactoring
refactor(components): extraire le composant bouton commun

# Performance
perf(database): optimiser la requête utilisateur avec l'indexation

# Tests
test(auth): ajouter des tests unitaires pour la validation de connexion

# Configuration
chore(deps): mettre à jour react vers la version 18.2.0

### Règles de Rédaction

1. **Utiliser l'impératif** : "add" au lieu de "added" ou "adds"
2. **Pas de point final** dans la description
3. **Première ligne max 50 caractères**
4. **Corps du message max 72 caractères par ligne**
5. **Séparer le sujet du corps par une ligne vide**
6. **Utiliser le corps pour expliquer le "quoi" et le "pourquoi"**

## 🚀 Commandes Git Utiles

### Configuration Initiale
```bash
# Configuration utilisateur
git config --global user.name "Votre Nom"
git config --global user.email "votre.email@example.com"

# Configuration de l'éditeur
git config --global core.editor "code --wait"

# Configuration des fins de ligne
git config --global core.autocrlf true  # Windows
git config --global core.autocrlf input # Mac/Linux
````

### Workflow Quotidien

```bash
# Vérifier le statut
git status

# Ajouter des fichiers
git add .
git add <fichier>

# Commit
git commit -m "feat(auth): add login functionality"

# Push
git push origin <branch-name>

# Pull avec rebase
git pull --rebase origin main
```

### Gestion des Branches

```bash
# Créer et basculer sur une nouvelle branche
git checkout -b feature/nouvelle-fonctionnalite

# Lister les branches
git branch -a

# Basculer sur une branche
git checkout main

# Supprimer une branche locale
git branch -d feature/ancienne-fonctionnalite

# Supprimer une branche distante
git push origin --delete feature/ancienne-fonctionnalite
```

### Historique et Logs

```bash
# Voir l'historique
git log --oneline
git log --graph --oneline --all

# Voir les changements
git diff
git diff --staged

# Voir les fichiers modifiés
git diff --name-only
```

### Annulation et Correction

```bash
# Annuler les changements non stagés
git checkout -- <fichier>
git restore <fichier>

# Annuler les changements stagés
git reset HEAD <fichier>
git restore --staged <fichier>

# Modifier le dernier commit
git commit --amend -m "nouveau message"

# Reset vers un commit précédent
git reset --soft HEAD~1  # Garde les changements
git reset --hard HEAD~1  # Supprime les changements
```

### Stash (Remisage)

```bash
# Sauvegarder les changements temporairement
git stash
git stash save "message descriptif"

# Lister les stash
git stash list

# Appliquer le dernier stash
git stash pop

# Appliquer un stash spécifique
git stash apply stash@{0}

# Supprimer un stash
git stash drop stash@{0}
```

### Merge et Rebase

```bash
# Merge une branche
git checkout main
git merge feature/ma-branche

# Rebase interactif
git rebase -i HEAD~3

# Rebase sur main
git checkout feature/ma-branche
git rebase main
```

### Commandes de Nettoyage

```bash
# Nettoyer les fichiers non trackés
git clean -fd

# Voir ce qui sera nettoyé
git clean -n

# Nettoyer les branches mergées
git branch --merged | grep -v "\*\|main\|develop" | xargs -n 1 git branch -d
```

## 🌿 Stratégie de Branches

### Git Flow Simplifié

- **main** : Branche de production
- **develop** : Branche de développement
- **feature/\*** : Nouvelles fonctionnalités
- **hotfix/\*** : Corrections urgentes
- **release/\*** : Préparation des releases

### Exemple de Workflow

1. Créer une branche feature depuis develop
2. Développer la fonctionnalité
3. Faire une pull request vers develop
4. Code review et merge
5. Deploy depuis main

## 🔍 Bonnes Pratiques

1. **Commits atomiques** : Un commit = une modification logique
2. **Messages clairs** : Expliquer le pourquoi, pas seulement le quoi
3. **Rebase avant merge** : Garder un historique propre
4. **Tests avant push** : S'assurer que le code fonctionne
5. **Pull requests** : Toujours passer par une review
6. **Branches courtes** : Éviter les branches qui vivent trop longtemps
7. **Synchronisation régulière** : Pull régulièrement depuis main/develop
