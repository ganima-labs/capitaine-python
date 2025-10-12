# Capitaine Python 🐍

Une plateforme d'apprentissage interactif pour enseigner Python aux débutants avec FastAPI et Docker.

## 📖 Description

Capitaine Python est un système éducatif complet qui permet aux débutants d'apprendre les fondamentaux de la programmation Python de manière interactive. L'application combine une API backend robuste avec une interface frontend simple pour créer une expérience d'apprentissage engageante.

### ✨ Caractéristiques principales

- **🎯 Cours progressifs** : 13 exercices structurés du niveau débutant à autonome
- **🌍 Multilinguisme** : Support français, anglais, espagnol, allemand
- **🔒 Exécution sécurisée** : Code exécuté dans un environnement isolé (Piston API)
- **📊 Suivi de progression** : Base de données SQLite pour tracer l'apprentissage
- **🧪 Tests complets** : 89% de couverture avec 379 tests unitaires
- **🐳 Conteneurisation** : Docker Compose pour un déploiement simplifié

## 🏗️ Architecture

### Backend FastAPI
```
app/
├── backend/
│   ├── main.py              # API FastAPI avec 4 endpoints
│   ├── exercises.py          # Définition des exercices pédagogiques
│   ├── grader.py            # Moteur d'éxécution sécurisée
│   ├── db.py                # Gestion SQLite de la progression
│   ├── security.py          # Validation et sécurité du code
│   └── course_manager.py    # Gestion des cours JSON
├── frontend/
│   ├── index.html           # Interface monopage
│   ├── app.js              # Logique JavaScript vanilla
│   └── style.css            # Style responsive
└── docker-compose.yml
```

### Points de terminaison de l'API
- `GET /api/exercises` - Liste tous les exercices disponibles
- `GET /api/exercises/{eid}` - Détails d'un exercice spécifique
- `POST /api/run` - Exécution simple (validation syntaxique)
- `POST /api/grade` - Validation complète avec tests unitaires

#### Endpoints de gestion des cours
- `GET /api/courses` - Liste tous les cours disponibles
- `GET /api/courses/{course_id}` - Détails complets d'un cours
- `GET /api/courses/{course_id}/exercises` - Liste des exercices d'un cours
- `GET /api/courses/{course_id}/exercises/{exercise_id}` - Détails d'un exercice spécifique
- `GET /api/courses/{course_id}/theme` - Thème visuel d'un cours
- `POST /api/courses/{course_id}/select` - Sélectionner un cours comme actif

#### Endpoints d'import de cours
- `POST /api/courses/import` - Importer un cours depuis une URL externe
- `POST /api/courses/import/file` - Importer un cours depuis un fichier JSON
- `DELETE /api/courses/{course_id}` - Supprimer un cours importé (protégé pour les cours intégrés)

## 📚 Structure des Cours

### Format JSON des Cours
Les cours sont stockés dans `app/backend/courses/` au format JSON structuré :

```json
{
  "meta": {
    "id": "python-basics",
    "title": {
      "fr": "Python les Bases - Édition Enrichie",
      "en": "Python Basics - Enhanced Edition"
    },
    "level": "débutant",
    "estimated_hours": 12,
    "prerequisites": [...],
    "learning_objectives": [...]
  },
  "theme": {
    "name": "ocean",
    "primary_color": "#0077be",
    "background_color": "#0a1929"
  },
  "exercises": [
    {
      "id": "01-print",
      "title": {...},
      "stars": 1,
      "prompt": {...},
      "starter": "code de départ",
      "theory": {
        "fr": {...},
        "en": {...}
      },
      "solution_explanation": {...},
      "why_important": {...},
      "further_exploration": {...},
      "cultural_note": {...},
      "tests": [...],
      "hints": {...}
    }
  ]
}
```

### Composants d'un Exercice

Chaque exercice inclut :
- **📝 Prompt** : Consigne claire et multilingue
- **🚀 Starter** : Code de départ pour guider l'apprenant
- **📚 Théorie** : Concepts, exemples, meilleures pratiques
- **💡 Solution** : Explication détaillée de la solution
- **🎯 Importance** : Contexte et applications réelles
- **🔍 Explorations** : Pistes pour aller plus loin
- **🌍 Note culturelle** : Anecdotes et contexte
- **✅ Tests** : Validation automatique de la solution
- **💡 Indices** : Aide progressive en cas de blocage

## 🚀 Installation et Démarrage

### Prérequis
- Docker et Docker Compose
- Git (optionnel, pour contribution)

### ✨ Nouvelle Fonctionnalité : Import de Cours

Capitaine Python prend désormais en charge l'import de cours depuis des sources externes, permettant d'étendre dynamiquement la plateforme avec de nouveaux contenus pédagogiques.

#### 🌐 Import depuis une URL
Importez des cours directement depuis GitHub, GitLab, Gist ou d'autres sources :

```bash
# Exemple d'import via API
curl -X POST http://localhost:8080/api/courses/import \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://raw.githubusercontent.com/user/course/main/course.json",
    "course_id": "mon-cours-personnalise",
    "overwrite": false
  }'
```

#### 📁 Import depuis un fichier
Téléversez manuellement des fichiers de cours JSON via l'interface web :

1. Cliquez sur "Importer un cours" dans l'interface
2. Choisissez "Importer depuis un fichier"
3. Sélectionnez votre fichier `.json`
4. Personnalisez l'ID si nécessaire
5. Cliquez sur "Importer"

#### 🔒 Sécurité Renforcée
- **Validation de domaine** : Seules les sources de confiance sont autorisées
- **Analyse de code** : Détection automatique des imports et fonctions dangereuses
- **Structure validation** : Vérification du format JSON et des champs obligatoires
- **Sandboxing** : Exécution isolée du code importé

#### 📋 Sources Supportées
- **GitHub** : `raw.githubusercontent.com`
- **GitLab** : Fichiers bruts GitLab
- **Gist** : `gist.githubusercontent.com`
- **Pastebin** : Services de partage de code
- **URLs locales** : Environnement de développement

#### 🎯 Workflow d'Import
1. **Aperçu** : Visualisez le contenu avant import
2. **Validation** : Vérification automatique de la structure
3. **Sécurité** : Analyse des menaces potentielles
4. **Import** : Ajout sécurisé à la plateforme
5. **Intégration** : Disponible immédiatement dans l'interface

### Installation rapide

1. **Cloner le dépôt**
```bash
git clone https://github.com/votre-username/capitaine-python.git
cd capitaine-python
```

2. **Démarrer l'environnement**
```bash
# Démarrage avec Docker Compose
docker-compose up --build -d

# Ou pour le développement avec rechargement automatique
docker-compose up --build --force-recreate
```

3. **Accéder à l'application**
- Interface web : http://localhost:8080
- API documentation : http://localhost:8080/docs

### Vérification de l'installation

```bash
# Vérifier que les services sont actifs
docker-compose ps

# Voir les logs de l'API
docker-compose logs -f api

# Tester l'API
curl http://localhost:8080/api/health
```

## 🧪 Tests

### Exécution des tests

```bash
# Depuis le répertoire racine
docker-compose exec api python -m pytest

# Avec couverture de code
docker-compose exec api python -m pytest --cov=. --cov-report=html

# Tests spécifiques
docker-compose exec api python -m pytest test_main.py -v
```

### Couverture de code actuelle

```
TOTAL                             4009    437    89%
main.py                               273    314    85%
secure_grader.py                       279    326    82%
security.py                             98    100    98%
db.py                                 66    198    66%
course_import.py                       156     45    71%
```

## 📖 Contenu Pédagogique

### Cours Actuel : Python les Bases (12h)

1. **Fais parler l'ordi** - `print()` et chaînes de caractères
2. **Trésor dans une variable** - Variables et typage dynamique
3. **Feu rouge/vert** - Conditions `if/elif/else`
4. **Compte 1 à 5** - Boucles `for` et `range()`
5. **Dis Bonjour** - Fonctions et `return`
6. **Addition magique** - Algorithmes et accumulateurs
7. **FizzBuzz rigolo** - Logique complexe et opérateurs
8. **Liste de courses magique** - Collections et listes
9. **Carte d'identité numérique** - Dictionnaires et paires clé-valeur
10. **Compte à rebours spatial** - Boucles `while`
11. **Détective logique** - Opérateurs `and/or/not`
12. **Division protégée** - Gestion des erreurs `try/except`
13. **Le plus grand** - Algorithmes de recherche simple

### Progression Pédagogique

- **🌱 Débutant** : Concepts fondamentaux, exemples concrets
- **🔍 Intermédiaire** : Combinaison de concepts, problèmes algorithmiques
- **⚡ Avancé** : Logique complexe, gestion d'erreurs, optimisation

## 🛠️ Développement

### Structure du Projet

```
capitaine-python/
├── app/                     # Application principale
│   ├── backend/              # API FastAPI
│   │   ├── main.py          # Point d'entrée API
│   │   ├── exercises.py      # Définition des exercices
│   │   ├── grader.py        # Évaluation du code
│   │   ├── db.py           # Base de données
│   │   ├── security.py     # Sécurité
│   │   └── course_manager.py # Gestion cours
│   └── frontend/             # Interface web
│       ├── index.html     # Page principale
│       ├── app.js         # Logique JavaScript
│       └── style.css       # Styles
├── app/backend/courses/      # Cours JSON
│   └── python-basics.json   # Cours principal
├── tests/                   # Tests backend
│   ├── test_main.py
│   ├── test_secure_grader_complete.py
│   ├── test_db_complete.py
│   └── test_security_complete.py
├── docker-compose.yml        # Configuration Docker
├── Dockerfile.backend       # Image backend
└── README.md               # Ce fichier
```

### Scripts Utiles

```bash
# Tests complets
docker-compose exec api python -m pytest --cov=. --cov-report=html

# Formatage du code
docker-compose exec api python -m black .

# Analyse de sécurité
docker-compose exec api python -m bandit -r .

# Tests de performance
docker-compose exec api python -m pytest tests/ -v --benchmark
```

## 🔧 Configuration

### Variables d'Environnement

```bash
# Configuration par défaut
DATABASE_URL=sqlite:///data/progress.db
PISTON_URL=http://piston:2000
API_HOST=0.0.0.0
API_PORT=8080
LOG_LEVEL=INFO
```

### Personnalisation

Pour ajouter un nouveau cours :
1. Créer un fichier JSON dans `app/backend/courses/`
2. Suivre le format structuré existant
3. Ajouter le cours à `course_manager.py`
4. Redémarrer l'application

Pour modifier les exercices existants :
1. Éditer `app/backend/courses/python-basics.json`
2. Respecter la structure JSON
3. Tester les modifications

## 📈 Monitoring et Logs

### Health Checks

- **API Health** : `GET /api/health`
- **Database** : Vérification de la connectivité SQLite
- **External Services** : Statut Piston API

### Logs

```bash
# Logs API en temps réel
docker-compose logs -f api

# Logs avec niveaux
docker-compose logs --tail=100 api | grep ERROR

# Logs de performance
docker-compose exec api python -m pytest --benchmark
```

## 🤝 Contribution

### Guidelines de Contribution

1. **Forker le projet**
2. **Créer une branche** (`git checkout -b feature/nouvelle-fonctionnalite`)
3. **Apporter les changements**
4. **Ajouter des tests** si nécessaire
5. **Soumettre une Pull Request**

### 🆕 Contribuer des Cours

Capitaine Python encourage la contribution communautaire de cours pédagogiques :

#### 📝 Créer un Cours
1. **Structure** : Suivez le format JSON documenté dans `docs/json-format-specification.md`
2. **Contenu** : Assurez-vous d'inclure théorie, exemples, et exercices progressifs
3. **Multilinguisme** : Au minimum français et anglais
4. **Tests** : Chaque exercice doit avoir des tests de validation
5. **Sécurité** : Le code doit être sécurisé et adapté aux débutants

#### 🔍 Validation avant Partage
```bash
# Tests de structure
python -m pytest tests/test_course_import.py -v

# Validation locale
curl -X POST http://localhost:8080/api/courses/import \
  -H "Content-Type: application/json" \
  -d '{"url": "file:///path/to/course.json"}'
```

#### 📚 Partager votre Cours
- **GitHub** : Hébergez votre fichier JSON et partagez l'URL brute
- **Interface** : Utilisez la fonction d'import intégrée
- **Communauté** : Soumettez votre cours pour inclusion dans la distribution principale

### Tests requis

- Tous les tests doivent passer
- Couverture de code minimale de 80%
- Code formaté avec `black`
- Respect des guidelines PEP 8

### Processus de Validation

1. **Linting** : `docker-compose exec api python -m flake8 .`
2. **Tests** : `docker-compose exec api python -m pytest`
3. **Sécurité** : `docker-compose exec api python -m bandit -r .`
4. **Performance** : Tests de charge si applicable

## 📝 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 🙏 Remerci

- **FastAPI** : Framework web moderne et performant
- **Piston** : Service d'exécution de code sécurisé
- **Docker** : Plateforme de conteneurisation
- **Python Community** : Écosystème riche et support

## 📞 Support

Pour toute question ou suggestion :
- Issues GitHub : [créer une issue](https://github.com/votre-username/capitaine-python/issues)
- Discussions : [discussions GitHub](https://github.com/votre-username/capitaine-python/discussions)

## 🔄 Mises à Jour Récentes

### Version 2.1 - Import de Cours Externes
- ✨ **Import depuis URL** : Importez des cours depuis GitHub, GitLab, Gist
- 📁 **Import depuis fichier** : Téléversez directement vos fichiers JSON
- 🔒 **Sécurité renforcée** : Validation avancée du contenu importé
- 👁️ **Aperçu en temps réel** : Visualisez les cours avant import
- 🎯 **Validation automatique** : Vérification structurelle et sécurité
- 📚 **Documentation complète** : Guides détaillés pour la création de cours

### Améliorations Techniques
- Tests complets pour la fonctionnalité d'import (71% couverture)
- API RESTful pour la gestion des cours
- Interface utilisateur moderne avec modales interactives
- Support multilingue amélioré

---

**🐍 Happy Learning with Capitaine Python!**

**📚 Ready to share your knowledge? Import or create courses today!**