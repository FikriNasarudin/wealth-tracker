# Wealth Tracker

A comprehensive full-stack Financial Tracker application built with Python, Django REST Framework, MySQL, and Vue.js.

This application allows you to track:
1. **Budgeting**: Income, Expenses, and spending weight breakdown.
2. **Investments**: Monthly portfolio snapshots, profit tracking, and asset allocation.
3. **Liabilities**: Loan tracking, debt reduction, and remaining principal balances.

## Prerequisites

Make sure you have the following installed in your environment (WSL/Ubuntu):
- Docker and Docker Compose (for MySQL database)
- Python 3.9+
- Node.js 18+ and npm

## Setup & Running Locally

### 1. Start the Database
The project uses a MySQL database hosted in a Docker container.
Run the following command from the root of the project to start it:
```bash
docker compose up -d
```

### 2. Run the Django Backend
Since this project runs in WSL, make sure to set up your Python virtual environment for Linux.

Navigate into the backend directory and set it up:
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Run the database migrations and start the server:
```bash
python manage.py migrate
python manage.py runserver
```
The backend API will now be running at `http://127.0.0.1:8000/`.

*(Optional)* Create a superuser to access the Django admin panel (`http://127.0.0.1:8000/admin/`):
```bash
python manage.py createsuperuser
```

### 3. Run the Vue.js Frontend
Open a new terminal window, navigate into the frontend directory, and set it up:

```bash
cd frontend
npm install
npm run dev
```

The frontend application will now be running, typically at `http://localhost:5173/`. 
Open this URL in your browser to view the application!

## Architecture Details

- **Backend**: Django 4.2+, Django REST Framework, Simple JWT for Authentication, MySQL.
- **Frontend**: Vue 3 (Composition API), Vite, Pinia (State Management), Vue Router, Axios, and Vanilla CSS with a premium design system.
