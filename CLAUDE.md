# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

Capitaine Python est une plateforme d'apprentissage interactif pour enseigner Python aux débutants. Le projet utilise une architecture client-serveur avec FastAPI en backend et du JavaScript vanilla en frontend, le tout containerisé avec Docker.

## Architecture

### Services Docker (3 services essentiels)
- **api** : Backend FastAPI avec interface web intégrée (port 8080)
- **piston** : Service d'exécution de code isolé (port 2000)
- **progress** : Volume persistant pour la base de données SQLite

### Backend (`app/backend/`)
- **main.py** : API FastAPI avec 4 endpoints principaux
  - `GET /api/exercises` : Liste tous les exercices disponibles
  - `GET /api/exercises/{eid}` : Détails d'un exercice spécifique
  - `POST /api/run` : Exécution simple du code (validation syntaxique)
  - `POST /api/grade` : Validation complète avec tests unitaires
- **exercises.py** : Définition des exercices pédagogiques avec prompts, starter code, tests et indices
- **grader.py** : Moteur d'exécution sécurisé utilisant Piston API (container d'isolation)
- **db.py** : Gestion de la persistance SQLite pour suivre la progression des apprenants

### Frontend (`app/frontend/`)
- **index.html** : Interface monopage avec éditeur de code et système d'exercices
- **app.js** : Logique JavaScript vanilla pour interagir avec l'API

### Infrastructure Simplifiée
- **Docker** : Containerisation légère avec 2 services seulement
- **Piston** : Service d'exécution de code isolé (utkashx/engineer-man-piston:latest)
- **SQLite** : Base de données légère pour la progression (persistée via volume)

## Commandes essentielles

### Développement local
```bash
# Démarrer l'environnement simplifié (API + Piston)
docker-compose up --build -d

# Arrêter les services
docker-compose down

# Voir les logs
docker-compose logs -f api

# Redémarrer après modifications
docker-compose up --build --force-recreate

# Nettoyer les anciens services monitoring si nécessaire
docker-compose down --remove-orphans
```

### Structure des exercices
Les exercices sont définis dans `app/backend/exercises.py` avec la structure :
- `id` : identifiant unique
- `title` : nom de l'exercice
- `stars` : difficulté (1-3 étoiles)
- `prompt` : consigne pour l'apprenant
- `starter` : code de départ
- `tests` : liste des tests de validation
- `hints` : indices en cas d'échec

### Ajouter un nouvel exercice
1. Modifier `app/backend/exercises.py`
2. Ajouter une nouvelle entrée dans la liste `EXERCISES`
3. Définir les tests en utilisant `run_with_input()` pour les exercices avec input
4. Utiliser `ns['function_name']()` pour tester les fonctions
5. Redémarrer avec `docker-compose up --build`

### Pistes de débuggage
- L'API backend tourne sur `http://localhost:8080`
- Le service Piston (exécution) est accessible sur `http://localhost:2000`
- Les données de progression sont persistées dans un volume Docker `progress`
- Pour vérifier la DB : `docker-compose exec api sqlite3 /data/progress.db`

## Environnement technique

- **Python 3.11** avec FastAPI, Uvicorn, httpx, pydantic
- **Frontend** : HTML5/CSS3/JavaScript vanilla (pas de framework)
- **Base de données** : SQLite avec persistances via volume Docker
- **Sécurité** : Exécution de code isolée via Piston API
- **Déploiement** : Docker Compose avec architecture légère (2 services)

## Accès aux services

- **Interface web** : http://localhost:8080
- **Documentation API** : http://localhost:8080/docs
- **Service Piston** : http://localhost:2000
- **Base de données** : `docker-compose exec api sqlite3 /data/progress.db`