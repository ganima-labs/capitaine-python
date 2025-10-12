# Guide de Contribution à Capitaine Python

Merci de votre intérêt pour contribuer à Capitaine Python ! Ce guide vous aidera à comprendre comment participer efficacement au développement de cette plateforme éducative.

## 🤝 Comment Contribuer

### Types de Contributions Attendues

1. **🐛 Correction de bugs** : Signaler et corriger des problèmes
2. **✨ Nouvelles fonctionnalités** : Ajouter des capacités à la plateforme
3. **📚 Contenu pédagogique** : Créer de nouveaux exercices et cours
4. **📖 Documentation** : Améliorer la documentation existante
5. **🧪 Tests** : Améliorer la couverture de tests
6. **🌍 Traduction** : Ajouter de nouvelles langues
7. **🎨 Design/UX** : Améliorer l'interface utilisateur

### Pour les Débutants

Si vous êtes nouveau dans le projet :

1. **Commencez par les issues "good first issue"** : Elles sont marquées comme faciles
2. **Lisez la documentation** : Familiarisez-vous avec l'architecture
3. **Installez l'environnement** : Suivez le guide d'installation
4. **Joignez-vous aux discussions** : Posez des questions dans GitHub Discussions

## 🚀 Processus de Contribution

### 1. Fork et Clonage

```bash
# 1. Forker le projet sur GitHub (bouton "Fork" en haut à droite)

# 2. Cloner votre fork localement
git clone https://github.com/VOTRE_USERNAME/capitaine-python.git
cd capitaine-python

# 3. Ajouter le dépôt original comme remote
git remote add upstream https://github.com/votre-username/capitaine-python.git

# 4. Vérifier la configuration
git remote -v
# origin    https://github.com/VOTRE_USERNAME/capitaine-python.git (fetch)
# upstream  https://github.com/votre-username/capitaine-python.git (fetch)
```

### 2. Configuration de l'Environnement

```bash
# 1. Créer une branche pour votre contribution
git checkout -b feature/nouvelle-fonctionnalite

# 2. Installer l'environnement de développement
docker-compose up --build -d

# 3. Vérifier que tout fonctionne
curl http://localhost:8080/api/health
```

### 3. Développement

#### Standards de Code

**Python (Backend)** :
- Respecter PEP 8
- Utiliser des noms de variables en anglais
- Ajouter des docstrings aux fonctions
- Type hints recommandés

```python
# Exemple de bonne pratique
def calculate_exercise_score(
    user_code: str,
    expected_output: str,
    test_cases: List[TestCase]
) -> ScoreResult:
    """
    Calculate the score for an exercise submission.

    Args:
        user_code: The code submitted by the user
        expected_output: The expected output
        test_cases: List of test cases to validate

    Returns:
        ScoreResult: Score and feedback
    """
    pass
```

**JavaScript (Frontend)** :
- Utiliser ES6+ features
- Noms de fonctions et variables en anglais
- Commentaires explicatifs

```javascript
// Exemple de bonne pratique
class ExerciseManager {
    constructor(apiClient) {
        this.apiClient = apiClient;
        this.currentExercise = null;
    }

    async loadExercise(exerciseId) {
        try {
            this.currentExercise = await this.apiClient.getExercise(exerciseId);
            return this.currentExercise;
        } catch (error) {
            console.error('Failed to load exercise:', error);
            throw error;
        }
    }
}
```

**JSON (Cours)** :
- Structure conforme à la spécification
- Contenu multilingue (français minimum, anglais recommandé)
- Validation avec le schéma JSON

#### Tests

**Tests Backend** :

```bash
# Exécuter tous les tests
docker-compose exec api python -m pytest

# Tests avec couverture
docker-compose exec api python -m pytest --cov=. --cov-report=html

# Tests spécifiques
docker-compose exec api python -m pytest test_main.py -v

# Tests de performance
docker-compose exec api python -m pytest --benchmark
```

**Tests Frontend** :

```bash
# Tests manuels via l'interface
# 1. Démarrer l'application
# 2. Tester chaque fonctionnalité
# 3. Vérifier la responsivité mobile
```

#### Validation du Code

```bash
# Formatage du code Python
docker-compose exec api python -m black .

# Vérification du style
docker-compose exec api python -m flake8 .

# Analyse de sécurité
docker-compose exec api python -m bandit -r .

# Tests de type (si mypy installé)
docker-compose exec api python -m mypy .
```

### 4. Commit et Push

#### Standards de Messages de Commit

Utilisez le format [Conventional Commits](https://www.conventionalcommits.org/) :

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

**Types courants** :
- `feat`: Nouvelle fonctionnalité
- `fix`: Correction de bug
- `docs`: Documentation
- `style`: Formatage, style
- `refactor`: Refactoring
- `test`: Tests
- `chore`: Maintenance

**Exemples** :

```bash
# Bon exemple
git commit -m "feat(api): add exercise completion tracking"

git commit -m "fix(frontend): resolve display issue on mobile devices"

git commit -m "docs(readme): update installation instructions for Windows"

git commit -m "test(py): add unit tests for security validator"
```

#### Processus de Commit

```bash
# 1. Ajouter les fichiers modifiés
git add .

# 2. Vérifier les changements
git status
git diff --staged

# 3. Commiter avec un message clair
git commit -m "feat(exercises): add string manipulation exercises"

# 4. Pusher vers votre fork
git push origin feature/nouvelle-fonctionnalite
```

### 5. Pull Request

#### Création de la Pull Request

1. **Allez sur GitHub** : Visitez votre fork sur GitHub
2. **Cliquez sur "New Pull Request"**
3. **Choisissez les branches** :
   - Base: `main` (dépôt original)
   - Compare: `votre-branche` (votre fork)
4. **Remplissez le template** : Utilisez le template fourni
5. **Cliquez sur "Create Pull Request"**

#### Template de Pull Request

```markdown
## Description
Brève description de la modification

## Type de Changement
- [ ] Bug fix (correction qui ne change pas les fonctionnalités existantes)
- [ ] New feature (ajout de fonctionnalité)
- [ ] Breaking change (modification qui casse la compatibilité)
- [ ] Documentation update

## Issue Connexe
Fixes #(numéro de l'issue)

## Tests
- [ ] J'ai testé manuellement
- [ ] J'ai ajouté des tests unitaires
- [ ] Tous les tests passent

## Vérification
- [ ] Le code suit les standards du projet
- [ ] La documentation est à jour
- [ ] Les messages de commit sont clairs
- [ ] J'ai testé sur différents navigateurs

## Captures d'Écran (si applicable)
Ajouter des captures d'écran pour les changements d'interface

## Questions/Remarques
Questions ou préoccupations concernant cette PR
```

#### Review Process

1. **Revue Automatique** : GitHub Actions vérifie les tests
2. **Revue Manuelle** : Un mainteneur examine votre code
3. **Feedback** : Suivez les suggestions et demandez des clarifications
4. **Approval** : Une fois approuvée, la PR sera mergée

## 📚 Types de Contributions Spécifiques

### 🐛 Correction de Bugs

#### Signaler un Bug

1. **Vérifier les issues existantes** : Éviter les doublons
2. **Utiliser le template Bug Report** :
```markdown
## Description du Bug
Description claire et concise

## Étapes pour Reproduire
1. Aller à...
2. Cliquer sur...
3. Voir l'erreur

## Comportement Attendu
Ce qui aurait dû se passer

## Comportement Actuel
Ce qui se passe réellement

## Environnement
- OS: [ex: Windows 10, macOS 12.0]
- Navigateur: [ex: Chrome 91, Firefox 89]
- Version: [ex: v2.1.0]

## Captures d'Écran
Si applicable, ajouter des captures d'écran

## Informations Additionnelles
Contexte supplémentaire
```

#### Corriger un Bug

1. **Reproduire le bug** : Comprendre exactement le problème
2. **Identifier la cause** : Localiser le code responsable
3. **Écrire un test** : Ajouter un test qui échoue avant la correction
4. **Corriger le code** : Implémenter la solution minimale
5. **Vérifier la correction** : Le test doit maintenant passer

### ✨ Nouvelles Fonctionnalités

#### Proposition de Fonctionnalité

1. **Vérifier les issues existantes** : Éviter les doublons
2. **Ouvrir une issue** avec le template Feature Request :
```markdown
## Description de la Fonctionnalité
Description claire de la fonctionnalité souhaitée

## Problème Résolu
Quel problème cette fonctionnalité résout-elle ?

## Solution Proposée
Description de la solution envisagée

## Alternatives Considérées
Autres approches envisagées

## Cas d'Usage
Exemples d'utilisation concrets

## Informations Additionnelles
Contexte supplémentaire
```

#### Implémentation

1. **Conception** : Planifier l'architecture de la fonctionnalité
2. **API d'abord** : Définir les endpoints si nécessaire
3. **Backend** : Implémenter la logique serveur
4. **Frontend** : Créer l'interface utilisateur
5. **Tests** : Couvrir tous les cas d'usage
6. **Documentation** : Mettre à jour la documentation

### 📚 Contenu Pédagogique

#### Créer un Nouvel Exercice

1. **Planification pédagogique** :
   - Objectif d'apprentissage clair
   - Progression logique
   - Niveau de difficulté approprié

2. **Structure de l'exercice** :
```json
{
  "id": "nouvel-exercice",
  "title": {
    "fr": "Titre de l'exercice",
    "en": "Exercise title"
  },
  "stars": 2,
  "prompt": {
    "fr": "Consigne claire et précise",
    "en": "Clear and precise instructions"
  },
  "starter": {
    "fr": "# Code de départ\nprint(\"À compléter\")",
    "en": "# Starter code\nprint(\"To complete\")"
  },
  "theory": {
    "fr": {
      "concept": "Concept principal",
      "explanation": "Explication détaillée",
      "examples": ["Exemple 1", "Exemple 2"],
      "best_practices": ["Pratique 1", "Pratique 2"],
      "common_mistakes": ["Erreur 1", "Erreur 2"]
    }
  },
  "solution_explanation": {
    "fr": "Explication de la solution"
  },
  "why_important": {
    "fr": "Importance et contexte réel"
  },
  "further_exploration": {
    "fr": ["Exploration 1", "Exploration 2"]
  },
  "tests": [
    {
      "description": "Test de validation",
      "code": "code_de_test",
      "expected_output": "résultat_attendu"
    }
  ],
  "hints": [
    {
      "level": 1,
      "text": {
        "fr": "Premier indice subtil"
      }
    }
  ]
}
```

3. **Validation** :
   - Tester l'exercice avec plusieurs solutions
   - Vérifier la clarté des instructions
   - S'assurer que les tests couvrent les cas limites

#### Créer un Nouveau Cours

1. **Définir le programme** :
   - Objectifs globaux
   - Structure des modules
   - Progression pédagogique

2. **Contenu multilingue** :
   - Au minimum français et anglais
   - Consistance entre langues
   - Adaptation culturelle si nécessaire

3. **Tests et validation** :
   - Tester tous les exercices
   - Vérifier la cohérence pédagogique
   - Obtenir des retours d'apprenants

### 🌍 Traduction

#### Ajouter une Nouvelle Langue

1. **Identifier les fichiers à traduire** :
   - `app/backend/courses/python-basics.json`
   - `app/frontend/index.html`
   - Documentation

2. **Standard de traduction** :
   - Utiliser les codes de langue ISO 639-1
   - Maintenir le ton éducatif
   - Adapter les exemples culturels

3. **Validation** :
   - Faire relire par un natif
   - Tester l'interface
   - Vérifier la cohérence

## 🏆 Reconnaissance des Contributeurs

### Hall of Fame

Les contributeurs sont reconnus dans :
- **README.md** : Section des contributeurs
- **Documentation** : Mentions spécifiques
- **Release notes** : Remerciements
- **GitHub** : Badges de contribution

### Types de Reconnaissance

- **🐛 Bug Hunter** : Corrections de bugs importantes
- **✨ Feature Master** : Fonctionnalités majeures
- **📚 Content Creator** : Contributions pédagogiques
- **🌍 Translator** : Support multilingue
- **🧪 Testing Champion** : Amélioration des tests
- **📖 Doc Hero** : Amélioration documentation

## 📋 Checklist de Contribution

### Avant de Commencer

- [ ] J'ai lu le guide de contribution
- [ ] J'ai cherché des issues similaires
- [ ] J'ai configuré mon environnement de développement
- [ ] Je comprends l'architecture du projet

### Pendant le Développement

- [ ] Mon code suit les standards du projet
- [ ] J'ai ajouté des tests pour mes modifications
- [ ] J'ai testé manuellement ma contribution
- [ ] J'ai vérifié la compatibilité mobile/desktop

### Avant la Pull Request

- [ ] Tous les tests passent
- [ ] Le code est formaté correctement
- [ ] La documentation est à jour
- [ ] Les messages de commit sont clairs

### Après la Pull Request

- [ ] J'ai répondu rapidement aux commentaires
- [ ] J'ai fait les modifications demandées
- [ ] J'ai testé les changements suggérés
- [ ] La PR est prête à être mergée

## 🆘 Obtenir de l'Aide

### Canaux de Communication

1. **GitHub Issues** : Pour les bugs et fonctionnalités
2. **GitHub Discussions** : Pour les questions générales
3. **Documentation** : Guides et références
4. **Code Review** : Feedback sur les Pull Requests

### Comment Poser une Bonne Question

1. **Décrire le contexte** : Ce que vous essayez de faire
2. **Montrer ce que vous avez essayé** : Code et approches
3. **Décrire le problème** : Ce qui ne fonctionne pas
4. **Fournir l'environnement** : OS, navigateur, version
5. **Être patient** : Les contributeurs sont bénévoles

## 📄 Licence

En contribuant à Capitaine Python, vous acceptez que vos contributions soient licenciées sous la même licence que le projet (MIT License).

---

Merci encore pour votre contribution ! Chaque participation, même petite, aide à rendre Capitaine Python meilleur pour la communauté des apprenants en programmation. 🐍✨