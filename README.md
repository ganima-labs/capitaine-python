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
- **👶 Mode enfant** : Interface adaptée pour les 8-12 ans avec gamification
- **📊 Monitoring avancé** : Docker health checks avec Prometheus/Grafana

## 🚀 Installation et Démarrage

### Prérequis
- Docker et Docker Compose
- Git (optionnel, pour contribution)

### Installation rapide

1. **Cloner le dépôt**
```bash
git clone https://github.com/vgadreau-pixel/capitaine-python.git
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

## 📚 Mode Enfant (Nouvelle fonctionnalité)

Capitaine Python dispose maintenant d'un mode spécialisé pour les enfants de 8-12 ans :

### 🎮 Caractéristiques Mode Enfant
- **🎨 Interface adaptée** : Design ludique et intuitif
- **🏆 Gamification** : Badges, avatars, progression visuelle
- **🔒 Sécurité renforcée** : Validation adaptée aux jeunes apprenants
- **👨‍👩‍👧‍👦 Dashboard parental** : Monitoring et contrôles parentaux
- **📈 Progression guidée** : Parcours pédagogique adapté

### 📊 Documentation complète
- `CHILD_MODE_IMPLEMENTATION_PLAN.md` - Roadmap 12 semaines
- `EXERCISE_PATTERNS_GUIDE.md` - Patterns sécurité/pédagogie
- `UI_DESIGN_PROPOSAL.md` - Design React/TypeScript
- `MONITORING_ADMIN.md` - Monitoring Docker

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

## 🤝 Contribution

### Guidelines de Contribution

1. **Forker le projet**
2. **Créer une branche** (`git checkout -b feature/nouvelle-fonctionnalite`)
3. **Apporter les changements**
4. **Ajouter des tests** si nécessaire
5. **Soumettre une Pull Request**

## 📝 Licence

Ce projet est sous licence MIT.

---

**🐍 Happy Learning with Capitaine Python!**