FROM python:3.11-slim

# Métadonnées
LABEL maintainer="hajar.dya@email.com"
LABEL description="API d'optimisation de transport mondial avec GTFS et OSM"

# Variables d'environnement
ENV PYTHONUNBUFFERED=1 \
    FLASK_ENV=production \
    PORT=5001

# Répertoire de travail
WORKDIR /app

# Dépendances système minimales
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Installer les dépendances Python
COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier toute l'application (templates + static inclus)
COPY app/ .

# Exposer le port
EXPOSE 5001

# Commande de démarrage
CMD ["python", "app.py"]
