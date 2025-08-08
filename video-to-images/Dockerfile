FROM python:3.8-slim

WORKDIR /app

# Installer les dépendances système pour FFmpeg
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Installer les dépendances Python
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copier le code de l'application dans le répertoire de travail du conteneur
COPY ./app /app

# Exposer le port
EXPOSE 5000

# Lancer Flask
CMD ["python", "/app/app.py"]
