# Utilise Python 3.11 comme base
FROM python:3.11-slim

# Définit le dossier de travail
WORKDIR /app

# Copie le contenu du projet
COPY . .

# Installe les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Lance ton bot
CMD ["python", "bot.py"]