# Usa Python 3.11 come base
FROM python:3.11-slim-bullseye

# Installa le librerie geografiche essenziali per PostGIS
RUN apt-get update && apt-get install -y \
    binutils libproj-dev gdal-bin python3-gdal \
    && rm -rf /var/lib/apt/lists/*

# Imposta la cartella di lavoro
WORKDIR /app

# Copia i requirements e installali
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia tutto il resto del codice
COPY . .

# Comando per avviare il server sulla porta richiesta da Render
CMD ["gunicorn", "core.wsgi:application", "--bind", "0.0.0.0:10000"]