# Backend — Wealth Tracker

This is the Django REST Framework backend for the Wealth Tracker application. It exposes a REST API consumed by the [Vue.js frontend](../frontend/README.md) and handles all data persistence via MySQL.

## 🧰 Tech Stack

- **Framework**: [Django](https://www.djangoproject.com/) + [Django REST Framework](https://www.django-rest-framework.org/)
- **Database**: MySQL
- **Auth**: Session / Token-based + Google OAuth 2.0 (optional)
- **Apps**: `budgeting`, `investments`, `liabilities`, `banking`, `goals`, `insights`, `users`

---

## 🛠️ Local Development

### 1. Start the Database
A local MySQL instance is provided via Docker Compose. From the project root:
```bash
docker compose up -d db
```

### 2. Set Up a Virtual Environment
Navigate into the `backend` directory and create an isolated Python environment:
```bash
cd backend
python3 -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment
The backend reads configuration from environment variables (or a `.env` file if you integrate `django-environ`). Key variables:

| Variable | Description | Default |
|---|---|---|
| `DB_HOST` | MySQL host | `localhost` |
| `DB_PORT` | MySQL port | `3306` |
| `DB_NAME` | Database name | — |
| `DB_USER` | Database user | — |
| `DB_PASSWORD` | Database password | — |
| `GOOGLE_CLIENT_ID` | Google OAuth Client ID | *(disabled)* |
| `SECRET_KEY` | Django secret key | — |
| `DEBUG` | Enable debug mode | `False` |

### 5. Apply Migrations
```bash
python manage.py migrate
```

*(Optional)* Create a superuser to access the Django admin panel:
```bash
python manage.py createsuperuser
```

### 6. Run the Development Server
```bash
python manage.py runserver
```

The API will be available at `http://localhost:8000`.
The admin panel is accessible at `http://localhost:8000/admin/`.

---

## 🐳 Docker

The backend is containerized with a single-stage Dockerfile using a Python base image.

To build and run the backend container in isolation:
```bash
docker build -t wealth-tracker-backend ./backend
docker run -p 8000:8000 wealth-tracker-backend
```

Or use Docker Compose from the project root (recommended), which also handles the database dependency:
```bash
docker compose up -d --build backend
```

Remember to run migrations after the first start:
```bash
docker compose exec backend python manage.py migrate
```
