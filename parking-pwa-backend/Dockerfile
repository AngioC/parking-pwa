# Usa una versione di Linux più recente e stabile (Bookworm)
FROM python:3.11-slim-bookworm

# Evita che il server si blocchi chiedendo conferme (S/N)
ENV DEBIAN_FRONTEND=noninteractive

# Installa le librerie spaziali essenziali per GeoDjango
RUN apt-get update && apt-get install -y \
    binutils \
    libproj-dev \
    gdal-bin \
    libgdal-dev \
    && rm -rf /var/lib/apt/lists/*

# Imposta la cartella di lavoro
WORKDIR /app

# Copia i requirements e installali
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia il codice
COPY . .

RUN python manage.py collectstatic --noinput

# Comando di avvio
CMD ["gunicorn", "core.wsgi:application", "--bind", "0.0.0.0:10000"]