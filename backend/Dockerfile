FROM python:3.11-slim

WORKDIR /app

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/main.py .
COPY backend/catalog.json .
COPY lineitem.parquet .
COPY piracicaba.json .
COPY Model/ ./Model/

RUN adduser --disabled-password --no-create-home appuser
USER appuser

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
