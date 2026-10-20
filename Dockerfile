# Origina en: ADR-001 (stack backend, sección "Empaquetado").
FROM python:3.11-slim

WORKDIR /app

# Dependencias desde el lockfile con hashes (versiones exactas y verificadas) y
# solo como wheels, para no ejecutar scripts de instalación. Única excepción:
# sgmllib3k (dependencia de feedparser), que solo se publica como código fuente.
# requirements.lock se genera desde requirements.txt (ver README).
COPY src/requirements.lock .
RUN pip install --no-cache-dir --require-hashes --only-binary :all: --no-binary sgmllib3k -r requirements.lock

COPY src/ .

# Migraciones de base de datos (Alembic). Se copian junto a la aplicación para
# que el contenedor cree o actualice las tablas de MySQL antes de arrancar la
# API. Sin esto, los endpoints de canales y fuentes fallan con "Table doesn't
# exist", porque nada creaba las tablas en MySQL.
COPY alembic/ ./alembic/
COPY alembic.ini .

# La API corre con un usuario sin privilegios (SonarQube: la imagen de Python
# usa root por defecto). Es dueño solo de /app/modelos, donde HU-SENT-006
# guarda los regresores entrenados (volumen modelos_ml de docker-compose).
RUN useradd --create-home --uid 10001 humworld \
    && mkdir -p /app/modelos \
    && chown humworld:humworld /app/modelos
USER humworld

EXPOSE 8000

CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
