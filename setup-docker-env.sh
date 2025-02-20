#!/bin/bash
set -e

echo "Setting up Docker deployment environment..."

# Rename settings files
if [ -f "etsu_office_hours/settings.py" ]; then
  echo "Renaming settings.py to settings_dev.py..."
  mv etsu_office_hours/settings.py etsu_office_hours/settings_dev.py

  # Create settings __init__.py to use the appropriate settings file
  cat > etsu_office_hours/settings/__init__.py << EOF
import os

if os.environ.get('DJANGO_SETTINGS_MODULE'):
    # Let the environment variable take precedence
    pass
elif os.environ.get('DJANGO_ENV') == 'production':
    from .settings_prod import *
else:
    from .settings_dev import *
EOF
fi

# Create necessary directories
echo "Creating necessary directories..."
mkdir -p static media logs nginx/ssl nginx/conf.d

# Copy settings_prod.py if it doesn't exist
if [ ! -f "etsu_office_hours/settings_prod.py" ]; then
  echo "Copying settings_prod.py..."
  cp path/to/settings_prod.py etsu_office_hours/settings_prod.py
fi

# Make sure .env file exists
if [ ! -f ".env" ]; then
  echo "Creating .env file from template..."
  cp .env.template .env
  echo "Please edit .env file with your secure values"
fi

# Generate SSL certificates if they don't exist
if [ ! -f "nginx/ssl/cert.pem" ]; then
  echo "Generating self-signed SSL certificates..."
  ./generate-ssl.sh
fi

echo "Setup complete! Next steps:"
echo "1. Edit .env file with secure values"
echo "2. Run 'docker-compose up -d --build' to start the services"
echo "3. Create a superuser with 'docker-compose exec web python manage.py createsuperuser'"