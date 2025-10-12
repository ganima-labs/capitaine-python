#!/usr/bin/env python3
"""
Capitaine Python Monitoring Watchdog
Service de surveillance avancée avec auto-récupération et alertes intelligentes
"""

import os
import sys
import json
import time
import logging
import requests
import docker
import schedule
from datetime import datetime, timedelta
from flask import Flask, jsonify, request
from prometheus_client import start_http_server, Counter, Histogram, Gauge
import threading

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/app/logs/watchdog.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Configuration
CONFIG = {
    'watchdog_interval': int(os.getenv('WATCHDOG_INTERVAL', '30')),
    'alert_webhook_url': os.getenv('ALERT_WEBHOOK_URL', 'http://alertmanager:9093/api/v1/alerts'),
    'telegram_bot_token': os.getenv('TELEGRAM_BOT_TOKEN'),
    'telegram_chat_id': os.getenv('TELEGRAM_CHAT_ID'),
    'email_to': os.getenv('EMAIL_TO'),
    'services_to_monitor': ['api', 'piston', 'prometheus', 'grafana', 'alertmanager'],
    'health_check_timeout': 10,
    'max_restart_attempts': 3,
    'restart_cooldown': 300  # 5 minutes
}

# Métriques Prometheus
METRICS = {
    'watchdog_runs_total': Counter('watchdog_runs_total', 'Total number of watchdog runs'),
    'service_checks_total': Counter('service_checks_total', 'Total service checks', ['service', 'status']),
    'service_restart_total': Counter('service_restart_total', 'Total service restarts', ['service']),
    'alerts_sent_total': Counter('alerts_sent_total', 'Total alerts sent', ['type']),
    'watchdog_duration_seconds': Histogram('watchdog_duration_seconds', 'Watchdog execution duration'),
    'services_healthy': Gauge('services_healthy', 'Number of healthy services'),
    'last_check_timestamp': Gauge('last_check_timestamp', 'Timestamp of last check')
}

# Flask pour les endpoints web
app = Flask(__name__)

class MonitoringWatchdog:
    def __init__(self):
        self.docker_client = None
        self.restart_history = {}
        self.last_alerts = {}

        try:
            self.docker_client = docker.from_env()
            logger.info("Connected to Docker socket")
        except Exception as e:
            logger.error(f"Failed to connect to Docker: {e}")
            sys.exit(1)

    def check_service_health(self, service_name):
        """Vérifie la santé d'un service"""
        try:
            container = self.docker_client.containers.get(f"capitaine-python-{service_name}-1")
            if container.status != 'running':
                return False, f"Container status: {container.status}"

            # Vérifier le health check du conteneur
            health = container.attrs.get('State', {}).get('Health', {})
            if health:
                status = health.get('Status', 'unknown')
                if status != 'healthy':
                    return False, f"Health check: {status}"

            return True, "Service is healthy"

        except docker.errors.NotFound:
            return False, "Container not found"
        except Exception as e:
            return False, f"Error checking service: {str(e)}"

    def restart_service(self, service_name):
        """Redémarre un service avec protection contre les boucles"""
        if service_name in self.restart_history:
            last_restart = self.restart_history[service_name]
            if time.time() - last_restart < CONFIG['restart_cooldown']:
                logger.warning(f"Service {service_name} restarted recently, skipping")
                return False, "Restart cooldown active"

        try:
            container = self.docker_client.containers.get(f"capitaine-python-{service_name}-1")

            logger.info(f"Restarting service {service_name}")
            container.restart()

            self.restart_history[service_name] = time.time()
            METRICS['service_restart_total'].labels(service=service_name).inc()

            # Attendre un peu que le service démarre
            time.sleep(10)

            # Vérifier que le service est maintenant healthy
            healthy, message = self.check_service_health(service_name)
            if healthy:
                logger.info(f"Service {service_name} restarted successfully")
                return True, "Restart successful"
            else:
                logger.error(f"Service {service_name} still unhealthy after restart: {message}")
                return False, f"Restart failed: {message}"

        except Exception as e:
            logger.error(f"Failed to restart service {service_name}: {e}")
            return False, f"Restart error: {str(e)}"

    def send_alert(self, alert_type, service_name, message, severity="warning"):
        """Envoie une alerte via différents canaux"""
        alert_key = f"{alert_type}_{service_name}"

        # Éviter les alertes en double
        if alert_key in self.last_alerts:
            if time.time() - self.last_alerts[alert_key] < 3600:  # 1 heure
                return

        self.last_alerts[alert_key] = time.time()

        alert_data = {
            "alerts": [
                {
                    "labels": {
                        "alertname": f"Watchdog{alert_type.title()}",
                        "service": service_name,
                        "severity": severity,
                        "instance": "watchdog"
                    },
                    "annotations": {
                        "summary": f"{alert_type.title()} alert for {service_name}",
                        "description": message
                    },
                    "startsAt": datetime.now().isoformat() + "Z",
                    "generatorURL": "http://watchdog:8082"
                }
            ]
        }

        # Envoyer à Alertmanager
        try:
            response = requests.post(
                CONFIG['alert_webhook_url'],
                json=alert_data,
                timeout=10
            )
            if response.status_code == 200:
                METRICS['alerts_sent_total'].labels(type='alertmanager').inc()
                logger.info(f"Alert sent to Alertmanager for {service_name}")
            else:
                logger.error(f"Failed to send alert to Alertmanager: {response.status_code}")
        except Exception as e:
            logger.error(f"Error sending alert to Alertmanager: {e}")

        # Envoyer à Telegram
        if CONFIG['telegram_bot_token'] and CONFIG['telegram_chat_id']:
            try:
                telegram_message = f"🚨 *{alert_type.title()} Alert* 🚨\n\n"
                telegram_message += f"*Service*: {service_name}\n"
                telegram_message += f"*Message*: {message}\n"
                telegram_message += f"*Time*: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

                response = requests.post(
                    f"https://api.telegram.org/bot{CONFIG['telegram_bot_token']}/sendMessage",
                    json={
                        'chat_id': CONFIG['telegram_chat_id'],
                        'text': telegram_message,
                        'parse_mode': 'Markdown'
                    },
                    timeout=10
                )
                if response.status_code == 200:
                    METRICS['alerts_sent_total'].labels(type='telegram').inc()
                    logger.info(f"Alert sent to Telegram for {service_name}")
            except Exception as e:
                logger.error(f"Error sending alert to Telegram: {e}")

    def run_health_checks(self):
        """Exécute les health checks sur tous les services"""
        start_time = time.time()
        METRICS['watchdog_runs_total'].inc()

        healthy_count = 0
        total_services = len(CONFIG['services_to_monitor'])

        for service_name in CONFIG['services_to_monitor']:
            try:
                healthy, message = self.check_service_health(service_name)

                if healthy:
                    logger.info(f"✅ {service_name}: {message}")
                    healthy_count += 1
                    METRICS['service_checks_total'].labels(service=service_name, status='healthy').inc()
                else:
                    logger.warning(f"❌ {service_name}: {message}")
                    METRICS['service_checks_total'].labels(service=service_name, status='unhealthy').inc()

                    # Tentative de redémarrage automatique
                    if service_name in ['api', 'piston']:  # Services critiques
                        restart_success, restart_message = self.restart_service(service_name)
                        if restart_success:
                            self.send_alert(
                                'service_restart',
                                service_name,
                                f"Service was unhealthy but has been restarted successfully: {restart_message}",
                                severity="info"
                            )
                        else:
                            self.send_alert(
                                'service_down',
                                service_name,
                                f"Service is unhealthy and restart failed: {message} | {restart_message}",
                                severity="critical"
                            )
                    else:
                        self.send_alert(
                            'service_unhealthy',
                            service_name,
                            f"Service is unhealthy: {message}",
                            severity="warning"
                        )

            except Exception as e:
                logger.error(f"Error checking service {service_name}: {e}")
                METRICS['service_checks_total'].labels(service=service_name, status='error').inc()
                self.send_alert(
                    'service_error',
                    service_name,
                    f"Error checking service: {str(e)}",
                    severity="critical"
                )

        # Mettre à jour les métriques
        METRICS['services_healthy'].set(healthy_count)
        METRICS['last_check_timestamp'].set(time.time())

        duration = time.time() - start_time
        METRICS['watchdog_duration_seconds'].observe(duration)

        logger.info(f"Health check completed: {healthy_count}/{total_services} services healthy ({duration:.2f}s)")

    def check_system_resources(self):
        """Vérifie les ressources système"""
        try:
            # CPU et mémoire du système hôte
            container = self.docker_client.containers.get("monitoring-watchdog")
            stats = container.stats(stream=False)

            # Utilisation CPU
            cpu_delta = stats['cpu_stats']['cpu_usage']['total_usage'] - stats['precpu_stats']['cpu_usage']['total_usage']
            system_cpu_delta = stats['cpu_stats']['system_cpu_usage'] - stats['precpu_stats']['system_cpu_usage']
            cpu_percent = (cpu_delta / system_cpu_delta) * len(stats['cpu_stats']['cpu_usage']['percpu_usage']) * 100

            # Utilisation mémoire
            memory_usage = stats['memory_stats']['usage']
            memory_limit = stats['memory_stats']['limit']
            memory_percent = (memory_usage / memory_limit) * 100

            if cpu_percent > 80:
                self.send_alert(
                    'high_cpu',
                    'system',
                    f"High CPU usage: {cpu_percent:.1f}%",
                    severity="warning"
                )

            if memory_percent > 90:
                self.send_alert(
                    'high_memory',
                    'system',
                    f"High memory usage: {memory_percent:.1f}%",
                    severity="warning"
                )

        except Exception as e:
            logger.error(f"Error checking system resources: {e}")

    def run_watchdog(self):
        """Fonction principale du watchdog"""
        logger.info("Starting watchdog run...")

        try:
            self.run_health_checks()
            self.check_system_resources()
        except Exception as e:
            logger.error(f"Error in watchdog run: {e}")
            self.send_alert(
                'watchdog_error',
                'watchdog',
                f"Watchdog encountered an error: {str(e)}",
                severity="critical"
            )

# Endpoints Flask
@app.route('/health')
def health():
    """Endpoint health pour le watchdog"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    })

@app.route('/metrics')
def metrics():
    """Endpoint Prometheus pour les métriques du watchdog"""
    from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}

@app.route('/webhook/alert', methods=['POST'])
def webhook_alert():
    """Webhook pour recevoir les alertes externes"""
    try:
        data = request.json
        logger.info(f"Received webhook alert: {data}")

        # Traitement spécifique selon le type d'alerte
        if 'service-down' in request.path:
            service_name = data.get('service', 'unknown')
            watchdog.send_alert(
                'external_service_down',
                service_name,
                f"External alert: Service {service_name} is down",
                severity="critical"
            )

        return jsonify({"status": "ok"}), 200

    except Exception as e:
        logger.error(f"Error processing webhook alert: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/status')
def status():
    """Endpoint de statut détaillé"""
    return jsonify({
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "config": CONFIG,
        "restart_history": watchdog.restart_history,
        "metrics": {
            "services_healthy": int(METRICS['services_healthy']._value._value),
            "last_check": float(METRICS['last_check_timestamp']._value._value)
        }
    })

def main():
    """Fonction principale"""
    global watchdog

    logger.info("Starting Capitaine Python Monitoring Watchdog")

    # Démarrer le serveur Prometheus
    start_http_server(8082)
    logger.info("Prometheus metrics server started on port 8082")

    # Initialiser le watchdog
    watchdog = MonitoringWatchdog()

    # Planifier les checks
    schedule.every(CONFIG['watchdog_interval']).seconds.do(watchdog.run_watchdog)

    # Exécuter le premier check immédiatement
    watchdog.run_watchdog()

    # Démarrer le serveur Flask dans un thread séparé
    flask_thread = threading.Thread(target=lambda: app.run(host='0.0.0.0', port=8082, debug=False))
    flask_thread.daemon = True
    flask_thread.start()

    logger.info("Watchdog started successfully")

    # Boucle principale
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Shutting down watchdog...")
    except Exception as e:
        logger.error(f"Fatal error in watchdog: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()