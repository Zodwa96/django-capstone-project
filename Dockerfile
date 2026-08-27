# Dockerfile for the News Application (Django capstone project)
FROM python:3.12-slim

# Don't write .pyc files, and flush stdout/stderr immediately so logs
# show up in `docker logs` right away.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# System packages required to build and run mysqlclient, per the
# official mysqlclient documentation for Debian/Ubuntu.
RUN apt-get update && apt-get install -y --no-install-recommends \
        python3-dev \
        default-libmysqlclient-dev \
        build-essential \
        pkg-config \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies first so this layer is cached unless
# requirements.txt actually changes.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the project source.
COPY . .

RUN chmod +x entrypoint.sh \
    && useradd --create-home appuser \
    && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

ENTRYPOINT ["./entrypoint.sh"]
