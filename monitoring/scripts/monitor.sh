#!/bin/bash
# Script de monitoring pour Capitaine Python
# Usage: ./monitor.sh [action] [options]

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"
COMPOSE_FILE="$PROJECT_DIR/docker-compose.yml"
LOG_FILE="/tmp/capitaine-python-monitor.log"

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fonctions utilitaires
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$LOG_FILE"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_FILE"
}

# Vérifier que Docker Compose est disponible
check_docker() {
    if ! command -v docker-compose &> /dev/null && ! command -v docker &> /dev/null; then
        error "Docker/Docker Compose n'est pas installé ou pas dans le PATH"
        exit 1
    fi

    # Utiliser docker compose si disponible, sinon docker-compose
    if command -v docker &> /dev/null && docker compose version &> /dev/null; then
        DOCKER_COMPOSE="docker compose"
    elif command -v docker-compose &> /dev/null; then
        DOCKER_COMPOSE="docker-compose"
    else
        error "Ni docker compose ni docker-compose n'est disponible"
        exit 1
    fi
}

# Afficher l'aide
show_help() {
    cat << EOF
Capitaine Python Monitoring Script

Usage: $0 [ACTION] [OPTIONS]

ACTIONS:
    status      Afficher le statut de tous les services
    health      Vérifier les health checks
    logs        Afficher les logs récents
    metrics     Afficher les métriques principales
    restart     Redémarrer un service spécifique
    cleanup     Nettoyer les ressources inutilisées
    backup      Créer une sauvegarde
    restore     Restaurer depuis une sauvegarde
    update      Mettre à jour les services
    help        Afficher cette aide

OPTIONS:
    --service SERVICE    Spécifier un service (pour restart, logs, etc.)
    --follow            Suivre les logs en temps réel
    --lines N           Nombre de lignes à afficher (défaut: 50)
    --verbose           Mode verbeux
    --quiet             Mode silencieux

EXEMPLES:
    $0 status
    $0 health
    $0 logs --service api --follow
    $0 restart --service piston
    $0 metrics
    $0 cleanup

EOF
}

# Afficher le statut des services
show_status() {
    log "Vérification du statut des services..."

    cd "$PROJECT_DIR"

    echo
    echo "=== STATUT DES SERVICES ==="
    $DOCKER_COMPOSE ps

    echo
    echo "=== DÉTAILS DES CONTENEURS ==="
    $DOCKER_COMPOSE ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}"

    echo
    echo "=== UTILISATION DES RESSOURCES ==="
    if command -v docker &> /dev/null && docker stats --no-stream &> /dev/null; then
        docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.BlockIO}}"
    else
        warning "docker stats n'est pas disponible"
    fi
}

# Vérifier les health checks
check_health() {
    log "Vérification des health checks..."

    cd "$PROJECT_DIR"

    # Vérifier les services individuellement
    services=("api" "piston" "prometheus" "grafana" "alertmanager" "nginx")

    for service in "${services[@]}"; do
        echo -n "[$service] "

        # Vérifier si le conteneur est en cours d'exécution
        if $DOCKER_COMPOSE ps -q "$service" | xargs docker inspect | jq -r '.[0].State.Status' 2>/dev/null | grep -q "running"; then
            # Vérifier le health check
            health_status=$($DOCKER_COMPOSE ps -q "$service" | xargs docker inspect | jq -r '.[0].State.Health.Status // "none"' 2>/dev/null)

            case "$health_status" in
                "healthy")
                    echo -e "${GREEN}✅ Healthy${NC}"
                    ;;
                "unhealthy")
                    echo -e "${RED}❌ Unhealthy${NC}"
                    ;;
                "none")
                    echo -e "${YELLOW}⚠️  No health check${NC}"
                    ;;
                "starting")
                    echo -e "${YELLOW}🔄 Starting${NC}"
                    ;;
                *)
                    echo -e "${RED}❓ Unknown ($health_status)${NC}"
                    ;;
            esac
        else
            echo -e "${RED}❌ Not running${NC}"
        fi
    done

    echo
    echo "=== TESTS DE CONNECTIVITÉ ==="

    # Test API
    if curl -s -f http://localhost:8080/api/health > /dev/null 2>&1; then
        echo -e "API: ${GREEN}✅ Accessible${NC}"
    else
        echo -e "API: ${RED}❌ Inaccessible${NC}"
    fi

    # Test Grafana
    if curl -s -f http://localhost:3001/api/health > /dev/null 2>&1; then
        echo -e "Grafana: ${GREEN}✅ Accessible${NC}"
    else
        echo -e "Grafana: ${RED}❌ Inaccessible${NC}"
    fi

    # Test Prometheus
    if curl -s -f http://localhost:9090/-/healthy > /dev/null 2>&1; then
        echo -e "Prometheus: ${GREEN}✅ Accessible${NC}"
    else
        echo -e "Prometheus: ${RED}❌ Inaccessible${NC}"
    fi
}

# Afficher les logs
show_logs() {
    local service=""
    local follow=false
    local lines=50

    # Parser les arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --service)
                service="$2"
                shift 2
                ;;
            --follow)
                follow=true
                shift
                ;;
            --lines)
                lines="$2"
                shift 2
                ;;
            *)
                shift
                ;;
        esac
    done

    cd "$PROJECT_DIR"

    local docker_args=("--tail=$lines")
    if [ "$follow" = true ]; then
        docker_args+=("--follow")
    fi

    if [ -n "$service" ]; then
        log "Affichage des logs du service $service..."
        $DOCKER_COMPOSE logs "${docker_args[@]}" "$service"
    else
        log "Affichage des logs de tous les services..."
        $DOCKER_COMPOSE logs "${docker_args[@]}"
    fi
}

# Afficher les métriques principales
show_metrics() {
    log "Collecte des métriques principales..."

    echo
    echo "=== MÉTRiques SYSTÈME ==="

    # Utilisation CPU et mémoire
    if command -v docker &> /dev/null && docker stats --no-stream &> /dev/null; then
        echo "Utilisation des ressources par conteneur:"
        docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}"
    fi

    echo
    echo "=== ESPACE DISQUE ==="
    df -h | grep -E "(Filesystem|/dev/)"

    echo
    echo "=== MÉTRIQUES APPLICATION ==="

    # Requêtes API si disponible
    if curl -s http://localhost:8080/api/health > /dev/null 2>&1; then
        echo "API Status: $(curl -s http://localhost:8080/api/health | jq -r '.status // unknown')"
    fi

    # Métriques Prometheus si disponible
    if curl -s http://localhost:9090/api/v1/query?query=up > /dev/null 2>&1; then
        echo "Services up:"
        curl -s http://localhost:9090/api/v1/query?query=up | jq -r '.data.result[] | "\(.metric.job): \(.value[1])"'
    fi

    echo
    echo "=== ALERTES ACTIVES ==="
    if curl -s http://localhost:9093/api/v1/alerts > /dev/null 2>&1; then
        active_alerts=$(curl -s http://localhost:9093/api/v1/alerts | jq '.data | length')
        echo "Alertes actives: $active_alerts"
    fi
}

# Redémarrer un service
restart_service() {
    local service=""

    while [[ $# -gt 0 ]]; do
        case $1 in
            --service)
                service="$2"
                shift 2
                ;;
            *)
                shift
                ;;
        esac
    done

    if [ -z "$service" ]; then
        error "Service requis avec --service"
        exit 1
    fi

    cd "$PROJECT_DIR"

    log "Redémarrage du service $service..."

    if $DOCKER_COMPOSE restart "$service"; then
        success "Service $service redémarré avec succès"

        # Attendre un peu que le service démarre
        sleep 10

        # Vérifier le statut
        if $DOCKER_COMPOSE ps -q "$service" | xargs docker inspect | jq -r '.[0].State.Status' 2>/dev/null | grep -q "running"; then
            success "Service $service est en cours d'exécution"
        else
            error "Le service $service n'a pas pu démarrer correctement"
        fi
    else
        error "Échec du redémarrage du service $service"
        exit 1
    fi
}

# Nettoyer les ressources
cleanup() {
    log "Nettoyage des ressources Docker..."

    # Supprimer les conteneurs arrêtés
    log "Suppression des conteneurs arrêtés..."
    docker container prune -f

    # Supprimer les images non utilisées
    log "Suppression des images non utilisées..."
    docker image prune -f

    # Supprimer les réseaux non utilisés
    log "Suppression des réseaux non utilisés..."
    docker network prune -f

    # Nettoyer les volumes (avec confirmation)
    read -p "Supprimer les volumes non utilisés ? (o/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Oo]$ ]]; then
        log "Suppression des volumes non utilisés..."
        docker volume prune -f
    fi

    success "Nettoyage terminé"
}

# Créer une sauvegarde
backup() {
    local backup_dir="$PROJECT_DIR/backups"
    local timestamp=$(date +'%Y%m%d_%H%M%S')
    local backup_file="$backup_dir/capitaine-python-backup-$timestamp.tar.gz"

    log "Création d'une sauvegarde..."

    mkdir -p "$backup_dir"

    cd "$PROJECT_DIR"

    # Arrêter les services pendant la sauvegarde
    log "Arrêt des services..."
    $DOCKER_COMPOSE down

    # Créer l'archive
    log "Création de l'archive de sauvegarde..."
    tar -czf "$backup_file" \
        --exclude='backups' \
        --exclude='node_modules' \
        --exclude='.git' \
        --exclude='monitoring/*/data' \
        .

    # Redémarrer les services
    log "Redémarrage des services..."
    $DOCKER_COMPOSE up -d

    success "Sauvegarde créée: $backup_file"

    # Nettoyer les anciennes sauvegardes (garder les 5 dernières)
    cd "$backup_dir"
    ls -t capitaine-python-backup-*.tar.gz | tail -n +6 | xargs -r rm
    log "Anciennes sauvegardes nettoyées"
}

# Mettre à jour les services
update() {
    cd "$PROJECT_DIR"

    log "Mise à jour des services..."

    # Récupérer les dernières images
    log "Récupération des dernières images Docker..."
    $DOCKER_COMPOSE pull

    # Recréer les services avec les nouvelles images
    log "Mise à jour des services..."
    $DOCKER_COMPOSE up -d --force-recreate

    # Vérifier le statut
    sleep 30
    check_health

    success "Mise à jour terminée"
}

# Analyse des logs d'erreurs
analyze_errors() {
    log "Analyse des erreurs dans les logs..."

    cd "$PROJECT_DIR"

    # Rechercher les erreurs dans les logs récents
    echo
    echo "=== ERREURS RÉCENTES ==="

    services=("api" "piston" "grafana" "prometheus" "alertmanager")

    for service in "${services[@]}"; do
        echo
        echo "[$service]:"
        $DOCKER_COMPOSE logs --tail=100 "$service" 2>&1 | grep -i error || echo "Aucune erreur détectée"
    done

    echo
    echo "=== ALERTES PROMETHEUS RÉCENTES ==="
    if curl -s http://localhost:9090/api/v1/query?query=ALERTS > /dev/null 2>&1; then
        curl -s http://localhost:9090/api/v1/query?query=ALERTS | jq -r '.data.result[] | "\(.labels.alertname): \(.annotations.summary)"'
    else
        echo "Prometheus non accessible"
    fi
}

# Fonction principale
main() {
    # Vérifier Docker
    check_docker

    # Créer le fichier de log
    mkdir -p "$(dirname "$LOG_FILE")"

    # Parser les arguments
    action="${1:-help}"
    shift

    case "$action" in
        status)
            show_status "$@"
            ;;
        health)
            check_health "$@"
            ;;
        logs)
            show_logs "$@"
            ;;
        metrics)
            show_metrics "$@"
            ;;
        restart)
            restart_service "$@"
            ;;
        cleanup)
            cleanup "$@"
            ;;
        backup)
            backup "$@"
            ;;
        update)
            update "$@"
            ;;
        errors)
            analyze_errors "$@"
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            error "Action inconnue: $action"
            show_help
            exit 1
            ;;
    esac
}

# Exécuter la fonction principale
main "$@"