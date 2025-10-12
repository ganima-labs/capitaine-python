# Guide d'Installation et d'Utilisation

Ce guide fournit des instructions complètes pour installer, configurer et utiliser la plateforme Capitaine Python dans différents environnements.

## 📋 Prérequis Système

### Configuration Minimale Recommandée

- **Système d'exploitation** : Windows 10+, macOS 10.15+, Ubuntu 18.04+
- **RAM** : 4 Go minimum (8 Go recommandés)
- **Stockage** : 2 Go d'espace libre
- **Processeur** : Architecture 64-bit (x86_64)

### Logiciels Requis

1. **Docker Desktop** (version 4.0+)
   - [Téléchargement Windows](https://www.docker.com/products/docker-desktop/)
   - [Téléchargement macOS](https://www.docker.com/products/docker-desktop/)
   - Installation Linux : `sudo apt-get install docker.io docker-compose`

2. **Git** (optionnel, pour le clonage)
   ```bash
   # Ubuntu/Debian
   sudo apt-get install git

   # macOS (via Homebrew)
   brew install git

   # Windows : Télécharger depuis git-scm.com
   ```

## 🚀 Installation Rapide

### Méthode 1 : Clonage depuis GitHub (Recommandé)

```bash
# 1. Cloner le dépôt
git clone https://github.com/votre-username/capitaine-python.git
cd capitaine-python

# 2. Démarrer l'environnement
docker-compose up --build -d

# 3. Vérifier l'installation
curl http://localhost:8080/api/health
```

### Méthode 2 : Téléchargement Direct

```bash
# 1. Télécharger et extraire l'archive
wget https://github.com/votre-username/capitaine-python/archive/main.zip
unzip main.zip
cd capitaine-python-main

# 2. Démarrer l'environnement
docker-compose up --build -d
```

## 🔧 Configuration Détaillée

### 1. Configuration Docker

#### Vérification de l'Installation Docker

```bash
# Vérifier Docker
docker --version
docker info

# Vérifier Docker Compose
docker-compose --version

# Tester Docker (doit afficher "Hello from Docker!")
docker run hello-world
```

#### Configuration des Ressources

Dans Docker Desktop :
- Allez dans **Settings** → **Resources**
- Allouez au minimum **4 GB RAM**
- Allouez au minimum **2 CPU cores**
- Activez **File sharing** pour le répertoire du projet

### 2. Variables d'Environnement

Créez un fichier `.env` à la racine du projet :

```bash
# Fichier .env
# Configuration de l'API
API_HOST=0.0.0.0
API_PORT=8080
LOG_LEVEL=INFO

# Base de données
DATABASE_URL=sqlite:///data/progress.db

# Service Piston (exécution de code)
PISTON_URL=http://piston:2000
PISTON_TIMEOUT=5

# Sécurité
MAX_CODE_LENGTH=10000
MAX_EXECUTION_TIME=5

# Développement
DEBUG=false
RELOAD=false
```

### 3. Configuration Réseau

#### Ports Utilisés

- **8080** : Interface web et API FastAPI
- **2000** : Service Piston (exécution sécurisée)
- **5432** : Base de données (si PostgreSQL utilisé)

#### Configuration Firewall

```bash
# Linux (ufw)
sudo ufw allow 8080/tcp
sudo ufw allow 2000/tcp

# macOS
# Les ports sont généralement ouverts par défaut

# Windows
# Configuration via Panneau de configuration → Pare-feu Windows
```

## 🎯 Lancement de l'Application

### Démarrage Standard

```bash
# Démarrer tous les services en arrière-plan
docker-compose up --build -d

# Vérifier le statut
docker-compose ps
```

### Démarrage pour Développement

```bash
# Démarrer avec rechargement automatique
docker-compose up --build --force-recreate

# Voir les logs en temps réel
docker-compose logs -f api
```

### Démarrage Sélectif

```bash
# Démarrer uniquement l'API
docker-compose up --build api

# Démarrer uniquement Piston
docker-compose up --build piston

# Démarrer avec profil de développement
docker-compose --profile dev up --build
```

## ✅ Vérification de l'Installation

### 1. Vérification des Services

```bash
# Vérifier que tous les conteneurs sont actifs
docker-compose ps

# Résultat attendu :
# NAME            COMMAND                  SERVICE             STATUS              PORTS
# api             "uvicorn main:app --…"   api                 running             0.0.0.0:8080->8080/tcp
# piston          "python -m api"          piston              running             0.0.0.0:2000->2000/tcp
```

### 2. Tests de Connectivité

```bash
# Test API FastAPI
curl http://localhost:8080/api/health
# Résultat attendu : {"status": "healthy", ...}

# Test Piston API
curl http://localhost:2000/runtimes
# Résultat attendu : liste des langages disponibles

# Test interface web
curl http://localhost:8080/
# Résultat attendu : contenu HTML de l'interface
```

### 3. Tests Fonctionnels

```bash
# Test chargement des exercices
curl http://localhost:8080/api/exercises

# Test exécution de code simple
curl -X POST http://localhost:8080/api/run \
  -H "Content-Type: application/json" \
  -d '{"code": "print(\"Hello World\")", "course_id": "python-basics"}'
```

## 🖥️ Utilisation de l'Application

### Accès aux Interfaces

1. **Interface Web principale** : http://localhost:8080
2. **Documentation API** : http://localhost:8080/docs
3. **API Piston** : http://localhost:2000

### Navigation dans l'Interface

1. **Page d'accueil** : Sélection du cours
2. **Interface d'exercice** :
   - Éditeur de code à gauche
   - Consignes et théorie à droite
   - Boutons d'exécution en bas
3. **Système de progression** :
   - Exercices complétés en vert
   - Exercice en cours en bleu
   - Exercices bloqués en gris

### Utilisation des Fonctionnalités

#### Éditeur de Code

```javascript
// Raccourcis clavier (si CodeMirror intégré)
Ctrl/Cmd + S    : Sauvegarder le code
Ctrl/Cmd + Enter: Exécuter le code
Ctrl/Cmd + /    : Commenter/décommenter
Tab             : Indenter
Shift + Tab     : Désindenter
```

#### Système d'Indices

- **1er indice** : Concept général
- **2ème indice** : Exemple de code
- **3ème indice** : Solution quasi complète

#### Feedback d'Exécution

- ✅ **Vert** : Test réussi
- ❌ **Rouge** : Test échoué avec message d'erreur
- ⚠️ **Orange** : Avertissement ou erreur non bloquante

## 🔍 Dépannage Commun

### Problèmes de Démarrage

#### 1. Port déjà utilisé

```bash
# Identifier le processus utilisant le port
lsof -i :8080  # macOS/Linux
netstat -ano | findstr :8080  # Windows

# Tuer le processus
kill -9 <PID>  # macOS/Linux
taskkill /PID <PID> /F  # Windows
```

#### 2. Échec de construction Docker

```bash
# Nettoyer le cache Docker
docker system prune -a

# Reconstruire depuis zéro
docker-compose down --volumes
docker-compose build --no-cache
docker-compose up -d
```

#### 3. Problèmes de permissions (Linux/macOS)

```bash
# Ajouter l'utilisateur au groupe docker
sudo usermod -aG docker $USER

# Recharger les groupes
newgrp docker

# Ou exécuter avec sudo (temporaire)
sudo docker-compose up -d
```

### Problèmes d'Exécution

#### 1. Piston API inaccessible

```bash
# Vérifier le statut du service Piston
docker-compose logs piston

# Redémarrer uniquement Piston
docker-compose restart piston

# Si Piston ne répond pas, l'API utilisera le fallback local
```

#### 2. Base de données inaccessible

```bash
# Vérifier les permissions du volume
ls -la data/

# Recréer la base de données
docker-compose down --volumes
docker-compose up -d api
```

#### 3. Erreurs de mémoire

```bash
# Augmenter la mémoire Docker dans les paramètres
# Docker Desktop → Settings → Resources → Memory

# Ou limiter les ressources utilisées
echo "DOCKER_MEMORY_LIMIT=2g" >> .env
```

### Problèmes de Performance

#### 1. Temps de réponse élevés

```bash
# Vérifier l'utilisation des ressources
docker stats

# Activer le mode développement pour le rechargement rapide
echo "RELOAD=true" >> .env
docker-compose restart api
```

#### 2. Espace disque insuffisant

```bash
# Nettoyer les images et conteneurs inutilisés
docker system prune -a --volumes

# Vérifier l'espace utilisé
docker system df
```

## 📊 Monitoring et Maintenance

### Logs de l'Application

```bash
# Voir tous les logs
docker-compose logs

# Logs spécifiques à l'API
docker-compose logs -f api

# Logs avec filtre
docker-compose logs api | grep ERROR

# Exporter les logs
docker-compose logs --no-color > application.log
```

### Surveillance de la Santé

```bash
# Health check automatique
curl http://localhost:8080/api/health

# Surveillance continue
watch -n 5 'curl -s http://localhost:8080/api/health | jq .'
```

### Sauvegarde des Données

```bash
# Sauvegarder la base de données
docker cp capitaine-python_api_1:/data/progress.db ./backup/

# Sauvegarder les fichiers de cours
cp -r app/backend/courses/ ./backup/

# Script de sauvegarde automatisé
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p backups/$DATE
docker cp capitaine-python_api_1:/data/progress.db backups/$DATE/
cp -r app/backend/courses/ backups/$DATE/
```

## 🔧 Configuration Avancée

### Personnalisation de l'Environnement

#### Configuration de Production

```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  api:
    environment:
      - DEBUG=false
      - LOG_LEVEL=WARNING
      - WORKERS=4
    deploy:
      resources:
        limits:
          memory: 512M
        reservations:
          memory: 256M
```

#### Configuration de Développement

```yaml
# docker-compose.dev.yml
version: '3.8'
services:
  api:
    environment:
      - DEBUG=true
      - LOG_LEVEL=DEBUG
      - RELOAD=true
    volumes:
      - ./app:/app
    command: uvicorn main:app --host 0.0.0.0 --port 8080 --reload
```

### Intégration CI/CD

#### GitHub Actions

```yaml
# .github/workflows/ci.yml
name: CI/CD Pipeline
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Build and test
        run: |
          docker-compose build
          docker-compose run --rm api python -m pytest
```

### Migration vers PostgreSQL

```yaml
# docker-compose.postgres.yml
services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: capitaine_python
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  api:
    environment:
      - DATABASE_URL=postgresql://postgres:password@postgres:5432/capitaine_python
```

## 📚 Ressources Additionnelles

### Documentation Complémentaire

- [Documentation FastAPI](https://fastapi.tiangolo.com/)
- [Documentation Docker](https://docs.docker.com/)
- [Documentation Piston](https://github.com/engineer-man/piston)
- [Guide SQLite](https://sqlite.org/docs.html)

### Communauté et Support

- **Issues GitHub** : Signaler des bugs et demander des fonctionnalités
- **Discussions** : Partager des astuces et poser des questions
- **Wiki** : Documentation communautaire et tutoriels

### Bonnes Pratiques

1. **Mettre à jour régulièrement** : `docker-compose pull && docker-compose up -d`
2. **Surveiller les logs** : `docker-compose logs -f` pendant le développement
3. **Sauvegarder avant les mises à jour** : Toujours conserver une copie des données
4. **Utiliser des environnements séparés** : Développement, test, production

Ce guide complet devrait permettre une installation et une utilisation sans problème de la plateforme Capitaine Python dans la plupart des environnements.