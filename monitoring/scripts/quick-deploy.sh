#!/bin/bash
# Script de déploiement rapide pour Capitaine Python avec monitoring
# Usage: ./quick-deploy.sh [environment]

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"
ENVIRONMENT="${1:-development}"

# Couleurs
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}✅${NC} $1"
}

warning() {
    echo -e "${YELLOW}⚠️${NC} $1"
}

error() {
    echo -e "${RED}❌${NC} $1"
}

# Vérification des prérequis
check_prerequisites() {
    log "Vérification des prérequis..."

    # Vérifier Docker
    if ! command -v docker &> /dev/null; then
        error "Docker n'est pas installé"
        exit 1
    fi

    # Vérifier Docker Compose
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        error "Docker Compose n'est pas installé"
        exit 1
    fi

    # Vérifier les ports disponibles
    ports=(80 443 8080 9090 9093 3001 3100)
    for port in "${ports[@]}"; do
        if lsof -i ":$port" &> /dev/null; then
            warning "Le port $port est déjà utilisé"
        fi
    done

    success "Prérequis vérifiés"
}

# Créer les fichiers de configuration
create_config_files() {
    log "Création des fichiers de configuration..."

    # Créer le fichier .env pour le monitoring
    cat > "$PROJECT_DIR/.env.monitoring" << EOF
# Configuration du monitoring Capitaine Python

# Telegram (optionnel)
TELEGRAM_BOT_TOKEN=votre_bot_token_ici
TELEGRAM_CHAT_ID=votre_chat_id_ici

# Email
ADMIN_EMAIL=admin@capitaine-python.com
EMAIL_USERNAME=votre_email@gmail.com
EMAIL_PASSWORD=votre_mot_de_passe_app

# Alertes
ALERT_WEBHOOK_URL=http://alertmanager:9093/api/v1/alerts

# Sécurité
PROMETHEUS_PASSWORD=prometheus123
GRAFANA_ADMIN_PASSWORD=admin123

# Monitoring
WATCHDOG_INTERVAL=30
EOF

    # Créer le fichier de mot de passe Nginx
    if ! docker run --rm httpd:2.4-alpine htpasswd -nb admin prometheus123 > "$PROJECT_DIR/monitoring/nginx/.htpasswd" 2>/dev/null; then
        # Fallback si httpd n'est pas disponible
        echo "admin:$(openssl passwd -apr1 prometheus123)" > "$PROJECT_DIR/monitoring/nginx/.htpasswd"
    fi

    # Créer les répertoires de données
    mkdir -p "$PROJECT_DIR/monitoring/data/"{prometheus,grafana,alertmanager,loki}

    success "Fichiers de configuration créés"
}

# Déployer l'infrastructure de monitoring
deploy_monitoring() {
    log "Déploiement de l'infrastructure de monitoring..."

    cd "$PROJECT_DIR"

    # Charger les variables d'environnement
    if [ -f "$PROJECT_DIR/.env.monitoring" ]; then
        export $(cat "$PROJECT_DIR/.env.monitoring | grep -v '^#' | xargs)
    fi

    # Déployer les services de monitoring en premier
    log "Démarrage des services de monitoring..."
    docker-compose up -d prometheus grafana alertmanager loki promtail node-exporter cadvisor

    # Attendre que les services de monitoring démarrent
    log "Attente du démarrage des services de monitoring..."
    sleep 30

    # Vérifier que les services de monitoring sont en cours d'exécution
    if docker-compose ps prometheus | grep -q "Up"; then
        success "Prometheus est en cours d'exécution"
    else
        error "Prometheus n'a pas démarré correctement"
    fi

    if docker-compose ps grafana | grep -q "Up"; then
        success "Grafana est en cours d'exécution"
    else
        error "Grafana n'a pas démarré correctement"
    fi

    # Déployer le watchdog
    log "Démarrage du monitoring watchdog..."
    docker-compose up -d monitoring-watchdog

    # Déployer les services de l'application
    log "Démarrage des services de l'application..."
    docker-compose up -d api piston

    # Déployer le reverse proxy
    log "Démarrage du reverse proxy..."
    docker-compose up -d nginx

    success "Infrastructure de monitoring déployée"
}

# Vérifier le déploiement
verify_deployment() {
    log "Vérification du déploiement..."

    cd "$PROJECT_DIR"

    # Attendre que tous les services soient prêts
    log "Attente de la disponibilité des services..."
    sleep 60

    # Vérifier les services
    services=("prometheus:9090" "grafana:3001" "alertmanager:9093" "api:8080")

    for service in "${services[@]}"; do
        IFS=':' read -r name port <<< "$service"
        if curl -s -f "http://localhost:$port" > /dev/null 2>&1; then
            success "$name est accessible sur le port $port"
        else
            warning "$name n'est pas encore accessible sur le port $port"
        fi
    done

    # Exécuter les health checks
    log "Exécution des health checks..."
    "$SCRIPT_DIR/monitor.sh" health
}

# Afficher les informations d'accès
show_access_info() {
    log "Informations d'accès :"

    echo
    echo "=== SERVICES PRINCIPAUX ==="
    echo "🚀 Capitaine Python: http://localhost:8080"
    echo "📊 Grafana: http://localhost:3001 (admin/admin123)"
    echo "📈 Prometheus: http://localhost:9090"
    echo "🚨 Alertmanager: http://localhost:9093"

    echo
    echo "=== SERVICES DE MONITORING ==="
    echo "📋 cAdvisor: http://localhost:8081"
    echo "📊 Node Exporter: http://localhost:9100/metrics"
    echo "📝 Loki: http://localhost:3100"

    echo
    echo "=== COMMANDES UTILES ==="
    echo "• Vérifier le statut: ./monitoring/scripts/monitor.sh status"
    echo "• Vérifier les health checks: ./monitoring/scripts/monitor.sh health"
    echo "• Voir les logs: ./monitoring/scripts/monitor.sh logs"
    echo "• Voir les métriques: ./monitoring/scripts/monitor.sh metrics"
    echo "• Redémarrer un service: ./monitoring/scripts/monitor.sh restart --service <nom>"

    echo
    echo "=== DASHBOARDS GRAFANA ==="
    echo "• Vue d'ensemble: http://localhost:3001/d/capitaine-python-overview"
    echo "• Métriques système: Disponible dans Grafana"
    echo "• Logs: Configurer Loki datasource dans Grafana"

    echo
    echo "🎉 Déploiement terminé !"
}

# Nettoyer en cas d'échec
cleanup_on_error() {
    error "Une erreur est survenue, nettoyage en cours..."
    cd "$PROJECT_DIR"
    docker-compose down
    exit 1
}

# Fonction principale
main() {
    log "Déploiement de Capitaine Python avec monitoring complet..."

    # Configuration du trap pour nettoyer en cas d'erreur
    trap cleanup_on_error ERR

    # Exécuter les étapes
    check_prerequisites
    create_config_files
    deploy_monitoring
    verify_deployment
    show_access_info

    success "Déploiement terminé avec succès !"
}

# Exécuter la fonction principale
main "$@"