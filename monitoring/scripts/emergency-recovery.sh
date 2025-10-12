#!/bin/bash
# Script de récupération d'urgence pour Capitaine Python
# Usage: ./emergency-recovery.sh [scenario]

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"
COMPOSE_FILE="$PROJECT_DIR/docker-compose.yml"
LOG_FILE="/tmp/capitaine-python-emergency-$(date +%Y%m%d_%H%M%S).log"

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[EMERGENCY]${NC} $1" | tee -a "$LOG_FILE"
}

success() {
    echo -e "${GREEN}[RECOVERED]${NC} $1" | tee -a "$LOG_FILE"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_FILE"
}

# Fonctions de récupération
recover_all_services_down() {
    log "Scénario: Tous les services sont down"

    cd "$PROJECT_DIR"

    # 1. Vérifier l'état de Docker
    log "Vérification de l'état de Docker..."
    if ! docker info > /dev/null 2>&1; then
        error "Docker n'est pas accessible. Veuillez vérifier le service Docker."
        return 1
    fi

    # 2. Nettoyer les conteneurs en erreur
    log "Nettoyage des conteneurs en erreur..."
    docker-compose down --remove-orphans || true

    # 3. Redémarrer les services critiques dans l'ordre
    log "Redémarrage des services critiques..."

    # Monitoring en premier
    log "Démarrage des services de monitoring..."
    docker-compose up -d prometheus grafana alertmanager

    sleep 30

    # Services applicatifs
    log "Démarrage des services applicatifs..."
    docker-compose up -d api piston

    sleep 30

    # Reverse proxy
    log "Démarrage du reverse proxy..."
    docker-compose up -d nginx

    # 4. Vérification
    log "Vérification des services..."
    sleep 30
    docker-compose ps

    success "Tentative de récupération terminée"
}

recover_api_down() {
    log "Scénario: Service API down"

    cd "$PROJECT_DIR"

    # 1. Forcer l'arrêt du conteneur API
    log "Arrêt forcé du conteneur API..."
    docker-compose kill api || true
    docker-compose rm -f api || true

    # 2. Nettoyer les ressources
    log "Nettoyage des ressources..."
    docker system prune -f

    # 3. Recréer le conteneur API
    log "Recréation du conteneur API..."
    docker-compose up -d api

    # 4. Attendre le démarrage
    log "Attente du démarrage de l'API..."
    sleep 60

    # 5. Vérifier le health check
    if docker-compose ps api | grep -q "healthy"; then
        success "API récupérée avec succès"
    else
        error "L'API n'est toujours pas healthy"
        return 1
    fi
}

recover_piston_down() {
    log "Scénario: Service Piston down"

    cd "$PROJECT_DIR"

    # 1. Forcer l'arrêt du conteneur Piston
    log "Arrêt forcé du conteneur Piston..."
    docker-compose kill piston || true
    docker-compose rm -f piston || true

    # 2. Nettoyer les données Piston si corrompues
    log "Nettoyage des données Piston..."
    docker volume rm capitaine-python_piston_data || true

    # 3. Recréer le conteneur Piston
    log "Recréation du conteneur Piston..."
    docker-compose up -d piston

    # 4. Attendre le démarrage
    log "Attente du démarrage de Piston..."
    sleep 60

    # 5. Vérifier le health check
    if docker-compose ps piston | grep -q "healthy"; then
        success "Piston récupéré avec succès"
    else
        error "Piston n'est toujours pas healthy"
        return 1
    fi
}

recover_high_memory_usage() {
    log "Scénario: Utilisation mémoire élevée"

    # 1. Identifier les conteneurs avec haute utilisation mémoire
    log "Identification des conteneurs avec haute utilisation mémoire..."
    docker stats --no-stream --format "table {{.Container}}\t{{.MemUsage}}\t{{.MemPerc}}" | head -10

    # 2. Redémarrer les services les plus gourmands
    log "Redémarrage des services critiques pour libérer la mémoire..."
    cd "$PROJECT_DIR"

    services_to_restart=("api" "piston" "prometheus")

    for service in "${services_to_restart[@]}"; do
        log "Redémarrage de $service..."
        docker-compose restart "$service"
        sleep 30
    done

    # 3. Nettoyer les ressources Docker
    log "Nettoyage des ressources Docker..."
    docker system prune -f
    docker volume prune -f

    success "Récupération mémoire terminée"
}

recover_disk_space_full() {
    log "Scénario: Espace disque plein"

    # 1. Afficher l'utilisation disque
    log "Analyse de l'utilisation disque..."
    df -h
    docker system df

    # 2. Nettoyer Docker de manière agressive
    log "Nettoyage agressif de Docker..."
    docker system prune -af
    docker volume prune -f

    # 3. Nettoyer les logs
    log "Nettoyage des logs..."
    sudo journalctl --vacuum-time=1d || true
    docker container logs $(docker container ls -aq) 2>&1 | sudo tee /dev/null || true

    # 4. Nettoyer les vieux backups
    log "Nettoyage des vieux backups..."
    find "$PROJECT_DIR/backups" -name "*.tar.gz" -mtime +7 -delete 2>/dev/null || true

    # 5. Nettoyer les données temporaires
    log "Nettoyage des fichiers temporaires..."
    sudo rm -rf /tmp/* 2>/dev/null || true
    rm -rf "$PROJECT_DIR"/monitoring/data/*/wal/* 2>/dev/null || true

    success "Nettoyage disque terminé"
}

recover_database_corruption() {
    log "Scénario: Base de données corrompue"

    cd "$PROJECT_DIR"

    # 1. Arrêter les services
    log "Arrêt des services..."
    docker-compose stop api piston

    # 2. Sauvegarder la base de données actuelle
    log "Sauvegarde de la base de données corrompue..."
    if docker-compose ps -q api | xargs docker exec ls /data/progress.db 2>/dev/null; then
        docker-compose exec api cp /data/progress.db /data/progress.db.corrupted.$(date +%Y%m%d_%H%M%S)
    fi

    # 3. Supprimer la base de données corrompue
    log "Suppression de la base de données corrompue..."
    docker-compose exec api rm -f /data/progress.db || true

    # 4. Redémarrer l'API pour recréer la base
    log "Redémarrage de l'API avec nouvelle base de données..."
    docker-compose up -d api

    # 5. Vérifier que la nouvelle base fonctionne
    sleep 30
    if docker-compose ps api | grep -q "healthy"; then
        success "Base de données recréée avec succès"
    else
        error "Échec de la recréation de la base de données"
        return 1
    fi
}

recover_monitoring_down() {
    log "Scénario: Services de monitoring down"

    cd "$PROJECT_DIR"

    # 1. Arrêter tous les services de monitoring
    log "Arrêt des services de monitoring..."
    docker-compose stop prometheus grafana alertmanager loki promtail monitoring-watchdog

    # 2. Nettoyer les données de monitoring corrompues
    log "Nettoyage des données de monitoring..."
    read -p "Supprimer les données de monitoring ? (o/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Oo]$ ]]; then
        docker volume rm capitaine-python_prometheus_data capitaine-python_grafana_data capitaine-python_alertmanager_data capitaine-python_loki_data || true
    fi

    # 3. Redémarrer les services de monitoring
    log "Redémarrage des services de monitoring..."
    docker-compose up -d prometheus grafana alertmanager loki promtail monitoring-watchdog

    # 4. Attendre le démarrage
    sleep 60

    # 5. Vérifier les services
    log "Vérification des services de monitoring..."
    docker-compose ps prometheus grafana alertmanager

    success "Services de monitoring récupérés"
}

# Diagnostic complet
run_diagnostic() {
    log "Diagnostic complet du système..."

    echo
    echo "=== SYSTÈME ==="
    uname -a
    df -h
    free -h

    echo
    echo "=== DOCKER ==="
    docker version
    docker-compose version
    docker system df

    echo
    echo "=== SERVICES ==="
    cd "$PROJECT_DIR"
    docker-compose ps

    echo
    echo "=== RESSOURCES ==="
    docker stats --no-stream

    echo
    echo "=== RÉSEAU ==="
    netstat -tlnp | grep -E ':(80|8080|9090|9093|3001|3100)'

    echo
    echo "=== LOGS D'ERREURS RÉCENTS ==="
    docker-compose logs --tail=20 | grep -i error || echo "Aucune erreur récente"

    success "Diagnostic terminé"
}

# Créer un backup d'urgence
create_emergency_backup() {
    log "Création d'un backup d'urgence..."

    local backup_dir="$PROJECT_DIR/emergency-backup-$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$backup_dir"

    cd "$PROJECT_DIR"

    # Backup des configurations
    log "Sauvegarde des configurations..."
    cp -r monitoring "$backup_dir/"
    cp docker-compose.yml "$backup_dir/"
    cp -r app "$backup_dir/"

    # Backup des volumes critiques
    log "Sauvegarde des volumes critiques..."
    docker run --rm -v capitaine-python_progress:/data -v "$backup_dir":/backup alpine tar czf /backup/progress.tar.gz -C /data .
    docker run --rm -v capitaine-python_piston_data:/data -v "$backup_dir":/backup alpine tar czf /backup/piston.tar.gz -C /data .

    # Backup des logs
    log "Sauvegarde des logs..."
    docker-compose logs --no-color > "$backup_dir/all-logs.txt"

    success "Backup d'urgence créé dans: $backup_dir"
}

# Afficher l'aide
show_help() {
    cat << EOF
Capitaine Python Emergency Recovery Script

Usage: $0 [SCENARIO]

SCENARIOS:
    all-down        Tous les services sont down
    api-down        Service API down
    piston-down     Service Piston down
    high-memory     Utilisation mémoire élevée
    disk-full       Espace disque plein
    db-corrupted    Base de données corrompue
    monitoring-down Services de monitoring down
    diagnostic      Diagnostic complet du système
    backup          Créer un backup d'urgence

EXEMPLES:
    $0 all-down
    $0 api-down
    $0 diagnostic
    $0 backup

EOF
}

# Fonction principale
main() {
    local scenario="${1:-help}"

    log "Script de récupération d'urgence Capitaine Python"

    case "$scenario" in
        all-down)
            recover_all_services_down
            ;;
        api-down)
            recover_api_down
            ;;
        piston-down)
            recover_piston_down
            ;;
        high-memory)
            recover_high_memory_usage
            ;;
        disk-full)
            recover_disk_space_full
            ;;
        db-corrupted)
            recover_database_corruption
            ;;
        monitoring-down)
            recover_monitoring_down
            ;;
        diagnostic)
            run_diagnostic
            ;;
        backup)
            create_emergency_backup
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            error "Scénario inconnu: $scenario"
            show_help
            exit 1
            ;;
    esac

    echo
    success "Opération terminée. Log disponible dans: $LOG_FILE"
}

# Exécuter la fonction principale
main "$@"