#!/bin/bash

# Create directory for SSL certificates
mkdir -p nginx/ssl

# Generate self-signed certificate for development
# In production, you would replace these with real certificates from Let's Encrypt or another provider
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout nginx/ssl/key.pem \
  -out nginx/ssl/cert.pem \
  -subj "/C=US/ST=Tennessee/L=Johnson City/O=ETSU/OU=Computing/CN=etsu-office-hours.example.com"

# Set appropriate permissions
chmod 600 nginx/ssl/key.pem
chmod 644 nginx/ssl/cert.pem

echo "Self-signed SSL certificates generated successfully."
echo "For production, replace these with proper certificates from your certificate authority."
