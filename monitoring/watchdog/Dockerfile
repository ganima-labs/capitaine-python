FROM python:3.11-slim

WORKDIR /app

# Installation des dépendances
RUN pip install docker requests prometheus-client flask schedule

# Copie des fichiers
COPY src/ /app/src/
COPY config/ /app/config/

# Création des répertoires de logs
RUN mkdir -p /app/logs

# Exposition du port
EXPOSE 8082

# Commande de démarrage
CMD ["python", "src/watchdog.py"]