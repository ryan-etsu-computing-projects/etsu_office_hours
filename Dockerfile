FROM python:3.12.2-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=etsu_office_hours.settings_prod

# Set work directory
WORKDIR /app

# Install dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create necessary directories
RUN mkdir -p /app/staticfiles /app/media /app/logs

# Copy project
COPY . .

# Run as non-root user for better security
RUN groupadd -r django && useradd -r -g django django
RUN chown -R django:django /app
USER django

# Run gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "etsu_office_hours.wsgi"]
