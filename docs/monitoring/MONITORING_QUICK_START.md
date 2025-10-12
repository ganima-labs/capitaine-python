# Guide de Démarrage Rapide - Monitoring Capitaine Python

## Installation en 5 Minutes

### 1. Prérequis

```bash
# Vérifier Docker
docker --version
docker-compose --version

# Ports requis : 80, 443, 8080, 9090, 9093, 3001, 3100
```

### 2. Déploiement

```bash
# Cloner et déployer
git clone <repository-url>
cd capitaine-python
./monitoring/scripts/quick-deploy.sh
```

### 3. Vérification

```bash
# Vérifier que tout fonctionne
./monitoring/scripts/monitor.sh health
```

## Accès Immédiat

| Service | URL | Login |
|---------|-----|-------|
| 🚀 Application | http://localhost:8080 | - |
| 📊 Grafana | http://localhost:3001 | admin/admin123 |
| 📈 Prometheus | http://localhost:9090 | admin/prometheus123 |
| 🚨 Alertes | http://localhost:9093 | - |

## Commandes Essentielles

```bash
# Vérifier le statut
./monitoring/scripts/monitor.sh status

# Voir les logs
./monitoring/scripts/monitor.sh logs --follow

# Redémarrer un service
./monitoring/scripts/monitor.sh restart --service api

# Voir les métriques
./monitoring/scripts/monitor.sh metrics
```

## En Cas de Problème

```bash
# Diagnostic complet
./monitoring/scripts/emergency-recovery.sh diagnostic

# Récupération d'urgence
./monitoring/scripts/emergency-recovery.sh all-down
```

## Prochaines Étapes

1. **Configurer les alertes** : Éditer `.env.monitoring`
2. **Explorer les dashboards** : Grafana → Dashboards
3. **Personnaliser** : Modifier `monitoring/prometheus/rules/`
4. **Documentation complète** : Voir `MONITORING_ADMIN.md`

---

🎉 **Félicitations !** Votre système de monitoring est opérationnel.