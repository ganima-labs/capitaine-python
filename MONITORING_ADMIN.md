# Documentation d'Administration - Monitoring Capitaine Python

## Vue d'Ensemble

Ce document décrit le système de monitoring complet mis en place pour Capitaine Python, incluant la supervision, les alertes, les logs centralisés et les procédures de dépannage.

## Architecture de Monitoring

### Services Déployés

1. **Prometheus** (port 9090) - Collecte de métriques
2. **Grafana** (port 3001) - Visualisation et dashboards
3. **Alertmanager** (port 9093) - Gestion des alertes
4. **Loki** (port 3100) - Logs centralisés
5. **Promtail** - Collecteur de logs
6. **Node Exporter** (port 9100) - Métriques système
7. **cAdvisor** (port 8081) - Métriques des conteneurs
8. **Monitoring Watchdog** (port 8082) - Surveillance active
9. **Nginx** (port 80/443) - Reverse proxy et load balancing

### Réseaux

- **capitaine-python-net** (172.21.0.0/16) - Services applicatifs
- **monitoring-net** (172.22.0.0/16) - Services de monitoring

## Installation et Déploiement

### Prérequis

- Docker et Docker Compose installés
- Ports disponibles : 80, 443, 8080, 9090, 9093, 3001, 3100
- 4GB RAM minimum recommandés
- 20GB espace disque disponible

### Déploiement Rapide

```bash
# Cloner le projet
git clone <repository-url>
cd capitaine-python

# Déployer avec monitoring complet
./monitoring/scripts/quick-deploy.sh
```

### Déploiement Manuel

```bash
# 1. Créer les fichiers de configuration
cp monitoring/.env.example .env.monitoring
# Éditer .env.monitoring avec vos informations

# 2. Démarrer les services
docker-compose up -d

# 3. Vérifier le déploiement
./monitoring/scripts/monitor.sh health
```

## Configuration

### Variables d'Environnement

Créer un fichier `.env.monitoring` à la racine du projet :

```bash
# Configuration Telegram (optionnel)
TELEGRAM_BOT_TOKEN=votre_bot_token
TELEGRAM_CHAT_ID=votre_chat_id

# Configuration Email
ADMIN_EMAIL=admin@capitaine-python.com
EMAIL_USERNAME=votre_email@gmail.com
EMAIL_PASSWORD=votre_mot_de_passe_app

# Configuration Alertes
ALERT_WEBHOOK_URL=http://alertmanager:9093/api/v1/alerts

# Configuration Sécurité
PROMETHEUS_PASSWORD=prometheus123
GRAFANA_ADMIN_PASSWORD=admin123

# Configuration Watchdog
WATCHDOG_INTERVAL=30
```

### Configuration des Alertes

Les alertes sont configurées dans `monitoring/prometheus/rules/alerts.yml` :

- **Alertes Critiques** : Services down, espace disque faible, attaques de sécurité
- **Alertes Warning** : Utilisation CPU/mémoire élevée, latence API
- **Alertes Info** : Faible engagement utilisateur

Les canaux de notification sont configurés dans `monitoring/alertmanager/alertmanager.yml` :

- Email
- Telegram
- Slack
- Webhooks personnalisés

## Utilisation Quotidienne

### Scripts de Monitoring

#### 1. Script Principal `monitor.sh`

```bash
# Vérifier le statut de tous les services
./monitoring/scripts/monitor.sh status

# Vérifier les health checks
./monitoring/scripts/monitor.sh health

# Voir les logs récents
./monitoring/scripts/monitor.sh logs

# Voir les logs d'un service spécifique
./monitoring/scripts/monitor.sh logs --service api --follow

# Afficher les métriques principales
./monitoring/scripts/monitor.sh metrics

# Redémarrer un service
./monitoring/scripts/monitor.sh restart --service piston

# Nettoyer les ressources
./monitoring/scripts/monitor.sh cleanup

# Créer une sauvegarde
./monitoring/scripts/monitor.sh backup

# Analyser les erreurs
./monitoring/scripts/monitor.sh errors
```

#### 2. Script de Récupération d'Urgence

```bash
# Récupération complète
./monitoring/scripts/emergency-recovery.sh all-down

# Récupération API
./monitoring/scripts/emergency-recovery.sh api-down

# Diagnostic complet
./monitoring/scripts/emergency-recovery.sh diagnostic

# Backup d'urgence
./monitoring/scripts/emergency-recovery.sh backup
```

### Accès aux Services

| Service | URL | Authentification |
|---------|-----|------------------|
| Capitaine Python | http://localhost:8080 | Aucune |
| Grafana | http://localhost:3001 | admin/admin123 |
| Prometheus | http://localhost:9090 | Basic auth |
| Alertmanager | http://localhost:9093 | Aucune |
| cAdvisor | http://localhost:8081 | Aucune |
| Node Exporter | http://localhost:9100/metrics | Aucune |

### Dashboards Grafana

1. **Vue d'Ensemble** : `/d/capitaine-python-overview`
   - État des services
   - Utilisation ressources
   - Métriques principales

2. **Métriques Système** :
   - CPU, mémoire, disque
   - Réseau
   - Conteneurs Docker

3. **Logs** :
   - Configurer datasource Loki
   - Filtrer par service
   - Recherche avancée

## Health Checks

### Configuration des Health Checks

Chaque service dispose de health checks personnalisés :

#### API Capitaine Python
- **Endpoint** : `/api/health`
- **Fréquence** : 15s
- **Timeout** : 10s
- **Vérifications** :
  - Réponse de l'API
  - Connectivité Piston
  - Accès base de données
  - Utilisation mémoire

#### Piston
- **Endpoint** : `/api/v2/runtimes`
- **Fréquence** : 15s
- **Timeout** : 10s
- **Vérifications** :
  - API accessible
  - Runtimes disponibles
  - Test d'exécution code
  - Espace disque

### États Possibles

- **healthy** : Service fonctionne correctement
- **unhealthy** : Service a des problèmes
- **starting** : Service en cours de démarrage
- **none** : Pas de health check configuré

## Alertes

### Niveaux de Sévérité

1. **Critical** : Intervention immédiate requise
   - Services down
   - Espace disque < 10%
   - Attaques de sécurité

2. **Warning** : Attention requise
   - CPU > 80%
   - Mémoire > 90%
   - Latence élevée

3. **Info** : Information uniquement
   - Faible engagement
   - Maintenance planifiée

### Canaux de Notification

#### Configuration Email
```yaml
smtp_smarthost: 'smtp.gmail.com:587'
smtp_from: 'alerts@capitaine-python.com'
smtp_auth_username: 'votre-email@gmail.com'
smtp_auth_password: 'votre-mot-de-passe-app'
```

#### Configuration Telegram
1. Créer un bot avec @BotFather
2. Obtenir le token
3. Créer un groupe/canal
4. Ajouter le bot et obtenir le chat_id

#### Configuration Slack
1. Créer un webhook Slack
2. Configurer dans `alertmanager.yml`

### Gestion des Alertes

#### Silence des Alertes
```bash
# Via Alertmanager UI
http://localhost:9093

# Via API
curl -X POST http://localhost:9093/api/v1/silences \
  -d '{"matchers":[{"name":"alertname","value":"ServiceDown","isRegex":false}],"startsAt":"2024-01-01T00:00:00Z","endsAt":"2024-01-01T01:00:00Z"}'
```

#### Maintenance Mode
```bash
# Mettre en mode maintenance
./monitoring/scripts/maintenance.sh enable --duration 2h

# Désactiver le mode maintenance
./monitoring/scripts/maintenance.sh disable
```

## Logs

### Architecture des Logs

1. **Loki** : Stockage centralisé des logs
2. **Promtail** : Collecte et parsing des logs
3. **Grafana** : Visualisation et recherche

### Configuration des Sources

- **Containers Docker** : `/var/lib/docker/containers/*/*log`
- **Logs système** : `/var/log/syslog`
- **API Capitaine Python** : Format JSON avec timestamps
- **Nginx** : Format de logs étendu
- **Monitoring** : Logs structurés

### Recherche de Logs

Via Grafana (Explore) :
```
{job="api"} |= "error"
{job="piston"} |= "timeout"
{service="api"} |~ "exception|error"
```

## Performance et Optimisation

### Métriques Clés à Surveiller

1. **Application** :
   - Temps de réponse API (95th percentile < 1s)
   - Taux d'erreurs (< 1%)
   - Requêtes par seconde

2. **Infrastructure** :
   - CPU (< 80%)
   - Mémoire (< 90%)
   - Espace disque (> 20% libre)

3. **Conteneurs** :
   - Nombre de conteneurs actifs
   - Utilisation ressources par conteneur
   - Redémarrages

### Optimisation

#### Resources Docker
```yaml
deploy:
  resources:
    limits:
      cpus: '1.0'
      memory: 512M
    reservations:
      cpus: '0.25'
      memory: 128M
```

#### Configuration Prometheus
```yaml
# Rétention des données
storage.tsdb.retention.time: 30d

# Scrape interval
scrape_interval: 15s
```

## Sécurité

### Mesures de Sécurité

1. **Isolation réseau** : Réseaux séparés pour monitoring et application
2. **Authentification** : Basic auth pour Prometheus, admin panel pour Grafana
3. **HTTPS** : Configuration SSL/TLS prête pour production
4. **Rate limiting** : Nginx rate limiting pour l'API
5. **Security headers** : Headers de sécurité dans Nginx

### Audit et Surveillance

1. **Logs d'accès** : Nginx access logs
2. **Alertes de sécurité** : Détection d'activités suspectes
3. **Monitoring des tentatives d'intrusion** : Analyse des logs d'erreurs

## Dépannage

### Problèmes Courants

#### Services Down
```bash
# Diagnostic
./monitoring/scripts/monitor.sh status

# Récupération
./monitoring/scripts/emergency-recovery.sh all-down
```

#### Haute Utilisation Mémoire
```bash
# Identifier les conteneurs
docker stats

# Récupération
./monitoring/scripts/emergency-recovery.sh high-memory
```

#### Espace Disque Plein
```bash
# Diagnostic
df -h
docker system df

# Nettoyage
./monitoring/scripts/emergency-recovery.sh disk-full
```

#### Base de Données Corrompue
```bash
# Récupération
./monitoring/scripts/emergency-recovery.sh db-corrupted
```

### Procédures de Support

#### 1. Collecte d'Informations
```bash
# Diagnostic complet
./monitoring/scripts/emergency-recovery.sh diagnostic

# Backup d'urgence
./monitoring/scripts/emergency-recovery.sh backup
```

#### 2. Escalade
- **Niveau 1** : Utiliser les scripts de récupération
- **Niveau 2** : Analyser les logs et métriques
- **Niveau 3** : Contact du support technique

#### 3. Documentation
- Documenter toutes les interventions
- Conserver les logs des diagnostics
- Mettre à jour la base de connaissances

## Maintenance

### Tâches Régulières

#### Quotidien
- Vérifier le statut des services
- Examiner les alertes critiques
- Surveiller l'utilisation des ressources

#### Hebdomadaire
- Nettoyer les logs anciens
- Vérifier les sauvegardes
- Analyser les tendances de performance

#### Mensuel
- Mettre à jour les conteneurs
- Revoir les configurations d'alertes
- Audit de sécurité

### Mises à Jour

#### Mise à Jour des Services
```bash
# Script de mise à jour automatique
./monitoring/scripts/monitor.sh update
```

#### Mise à Jour de Configuration
```bash
# Recharger configuration Prometheus
curl -X POST http://localhost:9090/-/reload

# Recharger configuration Alertmanager
curl -X POST http://localhost:9093/-/reload
```

## Sauvegarde et Restauration

### Stratégie de Sauvegarde

1. **Configurations** : Git repository
2. **Données utilisateur** : Volume Docker `progress`
3. **Données monitoring** : Volumes Docker dédiés
4. **Logs** : Centralisés dans Loki

### Sauvegarde Automatique
```bash
# Backup complet
./monitoring/scripts/monitor.sh backup

# Backup d'urgence
./monitoring/scripts/emergency-recovery.sh backup
```

### Restauration
```bash
# Restaurer depuis backup
./monitoring/scripts/restore.sh /path/to/backup.tar.gz

# Restaurer uniquement les données
./monitoring/scripts/restore.sh --data-only /path/to/backup.tar.gz
```

## Extensions et Évolutions

### Ajout de Nouveaux Services

1. Mettre à jour `docker-compose.yml`
2. Configurer les health checks
3. Ajouter les métriques Prometheus
4. Créer les dashboards Grafana
5. Configurer les alertes

### Scalabilité

1. **Horizontal scaling** : Load balancing avec Nginx
2. **Vertical scaling** : Ajustement des ressources Docker
3. **Monitoring scaling** : Distribution des charges

### Intégrations Possibles

- **ELK Stack** : Alternative à Loki
- **Jaeger** : Distributed tracing
- **Kubernetes** : Orchestration conteneurs
- **Cloud providers** : AWS, GCP, Azure monitoring

## Support et Contact

### Documentation Complémentaire

- `MONITORING_ADMIN.md` : Documentation administration
- `monitoring/scripts/` : Scripts automatisés
- `monitoring/prometheus/rules/` : Règles d'alertes
- README.md : Documentation générale

### Ressources Externes

- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [Docker Documentation](https://docs.docker.com/)

### Contact Support

Pour toute question ou problème :
- Email : admin@capitaine-python.com
- Documentation : https://docs.capitaine-python.com
- Issues : https://github.com/capitaine-python/issues

---

**Dernière mise à jour** : $(date +'%Y-%m-%d')
**Version** : 1.0.0
**Auteur** : Équipe Capitaine Python