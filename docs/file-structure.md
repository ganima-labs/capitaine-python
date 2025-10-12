# Structure des Fichiers de Capitaine Python

Ce document décrit en détail la structure complète des fichiers et répertoires du projet Capitaine Python.

## 📁 Structure Complète

```
capitaine-python/
│
├── 📄 README.md                    # Documentation principale du projet
├── 📄 CLAUDE.md                     # Instructions pour Claude Code
├── 📄 docker-compose.yml           # Configuration Docker Compose
├── 📄 Dockerfile.backend           # Image Docker pour le backend
│
├── 📁 app/                         # Application principale
│   │
│   ├── 📁 backend/                  # API FastAPI
│   │   ├──
│   │   ├── 📄 main.py              # Point d'entrée API (4 endpoints)
│   │   ├── 📄 exercises.py          # Définition des exercices
│   │   ├── 📄 grader.py            # Moteur d'évaluation sécurisé
│   │   ├── 📄 secure_grader.py     # Interface sécurisée pour Piston
│   │   ├── 📄 db.py                # Gestion SQLite de la progression
│   │   ├── 📄 security.py          # Validation et sécurité du code
│   │   ├── 📄 course_manager.py    # Gestion des cours JSON
│   │   │
│   │   ├── 📁 courses/              # Cours au format JSON
│   │   │   └── 📄 python-basics.json   # Cours principal (13 exercices)
│   │   │
│   │   └── 📁 data/                 # Données persistées (créé par Docker)
│   │       └── 📄 progress.db      # Base de données SQLite
│   │
│   └── 📁 frontend/                 # Interface web
│       ├── 📄 index.html           # Page principale monopage
│       ├── 📄 app.js              # Logique JavaScript vanilla
│       └── 📄 style.css            # Styles responsive
│
├── 📁 tests/                       # Tests backend
│   ├── 📄 test_main.py             # Tests API FastAPI
│   ├── 📄 test_secure_grader_complete.py  # Tests évaluation sécurisée
│   ├── 📄 test_db_complete.py      # Tests base de données
│   └── 📄 test_security_complete.py # Tests sécurité
│
└── 📁 docs/                        # Documentation additionnelle
    └── 📄 file-structure.md        # Ce fichier
```

## 📋 Description des Fichiers Principaux

### Fichiers Backend (`app/backend/`)

#### `main.py` - API FastAPI
**Rôle** : Point d'entrée de l'application web
**Endpoints** :
- `GET /api/exercises` - Liste tous les exercices disponibles
- `GET /api/exercises/{eid}` - Détails d'un exercice spécifique
- `POST /api/run` - Exécution simple (validation syntaxique)
- `POST /api/grade` - Validation complète avec tests unitaires

**Dépendances** : FastAPI, Uvicorn, course_manager, secure_grader, db, SecurityValidator

#### `exercises.py` - Définition des Exercices
**Rôle** : Structure des données pour chaque exercice pédagogique
**Contenu** : Liste d'exercices avec :
- `id` : identifiant unique (ex: "01-print")
- `title` : nom de l'exercice
- `stars` : difficulté (1-3 étoiles)
- `prompt` : consigne pour l'apprenant
- `starter` : code de départ
- `tests` : liste des tests de validation
- `hints` : indices progressifs

#### `grader.py` - Moteur d'Évaluation
**Rôle** : Évaluation du code soumis par les apprenants
**Fonctionnalités** :
- Validation syntaxique
- Exécution des tests unitaires
- Feedback structuré (succès/échec)
- Gestion des timeouts et erreurs

#### `secure_grader.py` - Interface Sécurisée
**Rôle** : Communication avec Piston API pour exécution isolée
**Sécurité** :
- Validation du code avant exécution
- Timeout configurable (5 secondes par défaut)
- Isolation dans conteneur Piston
- Fallback local si Piston indisponible

#### `db.py` - Gestion Base de Données
**Rôle** : Persistance des données de progression
**Fonctions** :
- Initialisation SQLite
- CRUD operations pour les exercices
- Suivi de progression des apprenants
- Gestion des erreurs de connexion

#### `security.py` - Validation de Sécurité
**Rôle** : Analyse et validation du code utilisateur
**Contrôles** :
- Imports interdits (os, system, subprocess, etc.)
- Fonctions dangereuses détectées
- Mots-clés sensibles identifiés
- Code malveillant bloqué

#### `course_manager.py` - Gestion des Cours
**Rôle** : Chargement et gestion des fichiers JSON de cours
**Fonctionnalités** :
- Chargement des fichiers JSON depuis `courses/`
- Validation du format des cours
- Accès aux exercices par ID
- Gestion multilingue

### Cours (`app/backend/courses/`)

#### `python-basics.json` - Cours Principal
**Rôle** : Cours complet "Python les Bases" (12h estimées)
**Structure** :
- Métadonnées : titre, niveau, prérequis, objectifs
- Thème visuel : couleurs, design
- 13 exercices progressifs du débutant à l'autonome

**Contenu par exercice** :
- Théorie multilingue (FR/EN/ES/DE)
- Exemples pratiques
- Meilleures pratiques
- Explications détaillées
- Tests de validation
- Indices progressifs

### Fichiers Frontend (`app/frontend/`)

#### `index.html` - Interface Principale
**Rôle** : Page web monopage pour l'apprentissage
**Composants** :
- Sélecteur de cours et d'exercices
- Éditeur de code avec coloration syntaxique
- Zone de sortie d'exécution
- Système d'indices et feedback
- Barre de progression

#### `app.js` - Logique JavaScript
**Rôle** : Interactivité et communication avec l'API
**Fonctionnalités** :
- Appels HTTP vers l'API FastAPI
- Gestion de l'état de l'interface
- Éditeur de code (CodeMirror ou natif)
- Affichage des résultats et erreurs
- Système de progression

#### `style.css` - Styles
**Rôle** : Design responsive et moderne
**Composants** :
- Layout adaptatif mobile/desktop
- Thème visuel cohérent
- Animations et transitions
- Coloration syntaxique
- Interface accessible

### Fichiers de Configuration

#### `docker-compose.yml` - Orchestration Docker
**Rôle** : Définition des services et infrastructure
**Services** :
- `api` : Application FastAPI (port 8080)
- `piston` : Service d'exécution sécurisée (port 2000)
- Volumes persistants pour les données

#### `Dockerfile.backend` - Image Backend
**Rôle** : Construction de l'image Docker pour l'API
**Base** : Python 3.11-slim
**Dépendances** : fastapi, uvicorn, httpx, pydantic, sqlite3

### Tests (`tests/`)

#### `test_main.py` - Tests API
**Couverture** : Endpoints FastAPI, gestion des erreurs, validation

#### `test_secure_grader_complete.py` - Tests Évaluation
**Couverture** : Exécution sécurisée, timeouts, isolation Piston

#### `test_db_complete.py` - Tests Base de Données
**Couverture** : CRUD operations, persistance, gestion erreurs

#### `test_security_complete.py` - Tests Sécurité
**Couverture** : Validation code, détection menaces, contrôles

## 🔄 Flux de Données

1. **Interface Utilisateur** → API FastAPI (`/api/exercises`, `/api/run`, `/api/grade`)
2. **API FastAPI** → Gestionnaire de Cours (`course_manager.py`)
3. **API FastAPI** → Évaluateur Sécurisé (`secure_grader.py`)
4. **Évaluateur** → Piston API (exécution isolée)
5. **API FastAPI** → Base de Données (`db.py`)
6. **Interface** → Mise à jour progression utilisateur

## 🛠️ Cycle de Développement

1. **Modification exercice** → Éditer `python-basics.json`
2. **Modification API** → Éditer fichiers Python dans `backend/`
3. **Tests** → `docker-compose exec api python -m pytest`
4. **Rebuild** → `docker-compose up --build --force-recreate`
5. **Vérification** → Accès `http://localhost:8080`

## 📊 État Actuel

- **13 exercices** dans le cours principal
- **89% couverture** avec 379 tests unitaires
- **4 langues** supportées (FR/EN/ES/DE)
- **Architecture** client-serveur complète
- **Sécurité** renforcée avec Piston API
- **Persistance** des données utilisateur

Cette structure modulaire permet une maintenance facile et une évolutivité pour ajouter de nouveaux cours et fonctionnalités.