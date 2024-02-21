FROM python:3.9

WORKDIR /app

# Se copia primero únicamente requirements.txt para aprovechar el caché de
# construcción de Docker, ANTES de observar los cambios de archivos del
# proyecto. Esto acelera la reconstrucción del container.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Utilizar Watchdog para el reinicio automático
CMD ["watchmedo", "auto-restart", "--directory=./", "--pattern=*.py", "--recursive", "--", "gunicorn", "--timeout", "120", "-b", ":5000", "app:app"]
