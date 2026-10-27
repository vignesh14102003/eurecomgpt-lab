
# Stage 1: Install Python dependencies
FROM python:3.11-slim AS builder

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


# Stage 2: Build the smaller runtime image
FROM python:3.11-slim

WORKDIR /app

COPY --from=builder /install /usr/local

COPY app.py .

ENV PORT=8080

EXPOSE 8080

CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "1", "--threads", "8", "app:app"]
