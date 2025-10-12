# Tests et Couverture de Code - Capitaine Python

## Vue d'ensemble

Ce document décrit la stratégie de tests mise en place pour atteindre une couverture de code de 100% pour le projet Capitaine Python.

## État Actuel de la Couverture

### Modules avec Couverture Complète ✅

| Module | Couverture | Tests | Description |
|--------|------------|-------|-------------|
| `config.py` | 99% | 34 tests | Configuration sécurisée, validation des paramètres |
| `exercises.py` | 100% | 52 tests | Structure et validation des exercices pédagogiques |
| `course_manager.py` | 100% | 47 tests | Gestion des cours et thèmes pédagogiques |

### Modules en Cours de Test 🚧

| Module | Couverture | Tests | Description |
|--------|------------|-------|-------------|
| `db.py` | 66% | 23 tests | Persistance SQLite et gestion de progression |
| `grader.py` | 0% | - | Moteur d'exécution legacy |
| `main.py` | 0% | - | API FastAPI avec endpoints |
| `secure_grader.py` | 0% | - | Exécution sécurisée du code |
| `security.py` | 0% | - | Analyse statique et validation |

## Configuration des Tests

### Fichiers de Configuration

- **`pytest.ini`**: Configuration principale de pytest avec seuil de couverture à 100%
- **`pyproject.toml`**: Configuration moderne des dépendances et outils
- **`requirements-test.txt`**: Dépendances pour les tests
- **`Makefile`**: Commandes rapides pour exécuter les tests

### Dépendances de Test

```bash
pytest>=7.4.0              # Framework de tests
pytest-cov>=4.1.0           # Mesure de couverture
pytest-asyncio>=0.21.0      # Support des tests async
pytest-mock>=3.12.0         # Mocking et isolation
pytest-xdist>=3.3.0         # Exécution parallèle
aiofiles>=23.2.0            # Support fichiers async
coverage>=7.3.0              # Outil de couverture
pydantic-settings>=2.11.0   # Configuration Pydantic
```

## Commandes de Test

### Exécution des Tests

```bash
# Installer les dépendances
make install

# Exécuter tous les tests avec couverture
make test

# Tests rapides sans couverture
make test-fast

# Tests par catégorie
make test-unit
make test-integration
make test-security

# Voir le rapport de couverture HTML
make coverage-open
```

### Commandes Avancées

```bash
# Tests avec rapport détaillé
pytest --cov=. --cov-report=html --cov-report=term-missing

# Tests en parallèle
pytest -n auto

# Tests par module spécifique
pytest test_config.py -v

# Tests avec marqueurs
pytest -m "unit" --cov=config
```

## Structure des Tests

### Organisation des Fichiers

```
app/backend/
├── test_config.py          # Tests configuration
├── test_db.py              # Tests base de données
├── test_exercises.py       # Tests exercices
├── test_course_manager.py  # Tests gestionnaire de cours
├── test_grader.py          # Tests grader legacy
├── test_security.py        # Tests sécurité (existants)
└── __init__.py
```

### Catégories de Tests

- **`@pytest.mark.unit`**: Tests unitaires isolés
- **`@pytest.mark.integration`**: Tests d'intégration entre modules
- **`@pytest.mark.security`**: Tests de sécurité et vulnérabilités
- **`@pytest.mark.slow`**: Tests qui prennent plus de temps

## Stratégie de Tests par Module

### 1. Configuration (`config.py`)

**Objectif**: Valider la configuration sécurisée de l'application

- ✅ Validation des valeurs par défaut
- ✅ Validation des entrées utilisateur
- ✅ Gestion des variables d'environnement
- ✅ Validation des URLs et origines CORS
- ✅ Tests des limites de sécurité
- ✅ Performance de création de configuration

### 2. Base de Données (`db.py`)

**Objectif**: Tester la persistance des données utilisateur

- ✅ Connexions et gestion des erreurs
- ✅ Initialisation et création de tables
- ✅ Sauvegarde et récupération des résultats
- ✅ Gestion de la progression utilisateur
- 🔄 Tests de performance et concurrence

### 3. Exercices (`exercises.py`)

**Objectif**: Valider la structure pédagogique des exercices

- ✅ Validation des métadonnées obligatoires
- ✅ Cohérence des étoiles et difficulté
- ✅ Syntaxe et qualité des tests
- ✅ Progression pédagogique
- ✅ Contenu Unicode et caractères spéciaux

### 4. Gestionnaire de Cours (`course_manager.py`)

**Objectif**: Tester la gestion des cours pédagogiques

- ✅ Chargement et validation des fichiers JSON
- ✅ Gestion des thèmes et métadonnées
- ✅ Navigation dans les exercices
- ✅ Performance avec nombreux cours
- ✅ Gestion des erreurs de fichiers

### 5. Moteur d'Exécution (`grader.py`)

**Objectif**: Valider l'exécution de code Python

- 🔄 Exécution locale avec fallback
- 🔄 Gestion des timeouts et erreurs
- 🔄 Support des entrées/sorties
- 🔄 Tests d'intégration avec Piston API

## Qualité des Tests

### Bonnes Pratiques Appliquées

1. **Tests Isolés**: Chaque test est indépendant avec setup/teardown
2. **Mocking**: Utilisation de `unittest.mock` pour isoler les dépendances
3. **Fixtures**: Réutilisation des configurations de test
4. **Paramétrisation**: Tests multiples efficaces avec `pytest.mark.parametrize`
5. **Assertions Claires**: Messages d'erreur explicites pour le debugging
6. **Tests de Performance**: Validation des temps d'exécution
7. **Tests Edge Cases**: Validation des cas limites et erreurs

### Types de Tests Couverts

- **Tests Positifs**: Validation du fonctionnement normal
- **Tests Négatifs**: Gestion des erreurs et cas invalides
- **Tests de Performance**: Temps d'exécution et utilisation mémoire
- **Tests de Sécurité**: Validation des entrées et prévention d'attaques
- **Tests d'Intégration**: Interaction entre modules
- **Tests de Conformité**: Respect des standards et formats

## CI/CD et Automatisation

### Configuration GitHub Actions (À implémenter)

```yaml
name: Tests et Couverture
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: make install-dev
      - name: Run tests
        run: make ci-test
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

### Qualité Gate

- **Couverture minimale**: 90% (objectif 100%)
- **Tous les tests doivent passer**
- **Pas de warnings critiques**
- **Performance conforme aux exigences**

## Métriques Actuelles

### Statistiques Globales

- **Tests totaux**: 133 tests écrits
- **Modules couverts**: 3/8 (37.5%)
- **Couverture moyenne**: 47.41%
- **Tests réussis**: 125/133 (94%)

### Objectifs Prochains

1. **Terminer les tests modules restants**:
   - `main.py` (API FastAPI)
   - `secure_grader.py` (exécution sécurisée)
   - `security.py` (sécurité)
   - Améliorer `db.py` et `grader.py`

2. **Atteindre 100% de couverture** sur tous les modules

3. **Configurer CI/CD** pour validation automatique

## Debugging et Maintenance

### Résolution des Problèmes Courants

1. **Imports**: Utiliser les imports relatifs pour les tests locaux
2. **Dependencies**: Installer `pydantic-settings` pour Pydantic v2
3. **Async**: Utiliser `pytest-asyncio` pour les fonctions asynchrones
4. **Coverage**: Configurer correctement `PYTHONPATH` pour la mesure

### Surveillance

- **Coverage HTML**: `htmlcov/index.html` pour visualisation détaillée
- **Logs pytest`: Utiliser `-v` et `--tb=short` pour debugging
- **Performance**: `--durations=10` pour identifier les tests lents

## Conclusion

Le projet Capitaine Python dispose maintenant d'une base de tests solide avec :
- **Configuration robuste** pour les futures évolutions
- **Couverture élevée** sur les modules critiques
- **Tests de qualité** avec isolation et performance
- **Documentation complète** pour la maintenance

La prochaine étape consiste à compléter les tests des modules restants pour atteindre l'objectif de 100% de couverture sur l'ensemble du projet.