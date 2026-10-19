# Origina en: ADR-001 (stack backend, sección "Empaquetado").
FROM python:3.11-slim

WORKDIR /app

COPY src/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ .

# Migraciones de base de datos (Alembic). Se copian junto a la aplicación para
# que el contenedor cree o actualice las tablas de MySQL antes de arrancar la
# API. Sin esto, los endpoints de canales y fuentes fallan con "Table doesn't
# exist", porque nada creaba las tablas en MySQL.
COPY alembic/ ./alembic/
COPY alembic.ini .

EXPOSE 8000

CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
