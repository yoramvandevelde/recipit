# Recipit - Personal Recipe Manager

A self-hosted web application for managing recipes with cook mode, shopping list integration, and automatic Docker builds.

## Features

-  Create, edit, and delete recipes
-  Search recipes by title, ingredients, or tags
-  Cook mode with distraction-free ingredient panel
-  Add ingredients to HomeAssistant shopping list
-  Tag recipes for easy organization
-  Mobile-friendly PWA
-  Database backup/restore via admin panel
-  Password-protected access

## Quick Start with Docker

```bash
docker run -d \
  -p 5000:5000 \
  -v ./data:/srv/data \
  -e ADMIN_USER=admin \
  -e ADMIN_PASSWORD_HASH='<bcrypt_hash>' \
  -e SECRET_KEY='<random_hex>' \
  ghcr.io/yoramvandevelde/recipit:latest
```

## Environment Variables

| Variable	| Description |
| -----------|------------------
| ADMIN_USER |	Admin username (default: admin)"|
| ADMIN_PASSWORD_HASH	| bcrypt hash of password
|SECRET_KEY	| Flask session encryption key
|DATABASE_PATH	| Database file location (default: recepten.db)
|HA_URL	| HomeAssistant URL (optional)
|HA_TOKEN |	HomeAssistant access token (optional)

## Generate Credentials
```bash
# Generate password hash
python -c "import bcrypt; print(bcrypt.hashpw(b'your_password', bcrypt.gensalt()).decode())"

# Generate secret key
python -c "import secrets; print(secrets.token_hex(32))"

## Development
```bash
git clone <repository>
cd recipit
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```
The application will be available at http://localhost:5000

## Tech Stack
- Backend: Flask, SQLite
- Frontend: Vanilla JS, CSS variables
- Auth: Flask-Login + bcrypt
- Deployment: Docker + GitHub Actions

