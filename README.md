# Wealth Tracker

A comprehensive full-stack Financial Tracker application built with Python, Django REST Framework, MySQL, and Vue.js.

This application allows you to track:
1. **Budgeting**: Income, Expenses, and spending weight breakdown.
2. **Investments**: Monthly portfolio snapshots, profit tracking, and asset allocation.
3. **Liabilities**: Loan tracking, debt reduction, and remaining principal balances.

---

## 🚀 Homelab Deployment (Docker Compose)

Wealth Tracker is built for containerized environments. The easiest and officially supported way to run the application is using Docker Compose. 

### 1. Prerequisites
Ensure you have Docker and Docker Compose installed on your system.

### 2. Installation
Clone the repository to your server:
```bash
git clone https://github.com/FikriNasarudin/wealth-tracker.git
cd wealth-tracker
```

### 3. Start the Application
Bring up the entire stack (Database, Backend, and Frontend). By default, this will automatically build the container images from the source code locally:
```bash
docker compose up -d --build
```

### 4. Initialize the Database
Because this is your first time running the application, you must initialize the database tables:
```bash
docker compose exec backend python manage.py migrate
```

*(Optional)* Create an administrative user to access the Django backend panel:
```bash
docker compose exec backend python manage.py createsuperuser
```

### 5. Access the Application
You can now access the Wealth Tracker application in your web browser!
- **Frontend Dashboard**: `http://<your-server-ip>/`
- **Backend Admin Panel**: `http://<your-server-ip>:8000/admin/`

### 6. (Optional) Enable Google Login
Google Login is disabled by default. To enable it:
1. Create OAuth 2.0 Credentials in the [Google Cloud Console](https://console.cloud.google.com/).
2. Add your server's URI to the "Authorized JavaScript origins" (e.g., `http://your-server-ip:80`).
3. Open `docker-compose.yml` and replace the empty `GOOGLE_CLIENT_ID` and `VITE_GOOGLE_CLIENT_ID` values with your generated Client ID.
4. Rebuild the stack:
   ```bash
   docker compose up -d --build
   ```

---

## 🏗️ Advanced Kubernetes Deployment (K3s, Minikube, Proxmox)

For advanced homelab users, standard Kubernetes manifests are provided.

1. Apply the Persistent Volume and MySQL Deployment:
   ```bash
   kubectl apply -f k8s/mysql-deployment.yaml
   ```
2. Apply the Backend and Frontend Deployments:
   ```bash
   kubectl apply -f k8s/backend-deployment.yaml
   kubectl apply -f k8s/frontend-deployment.yaml
   ```
3. Apply the Ingress rules (ensure you have an Ingress controller like NGINX installed):
   ```bash
   kubectl apply -f k8s/ingress.yaml
   ```
4. Initialize the database by getting the backend pod name:
   ```bash
   kubectl get pods -l app=backend
   kubectl exec -it <backend-pod-name> -- python manage.py migrate
   ```

---

## 🛠️ Local Development (Contributors)

If you want to contribute to the code or run it locally for testing:

### 1. Start the Database
Start the MySQL container locally:
```bash
docker compose up -d db
```

### 2. Run the Django Backend
Navigate into the `backend` directory and set up a Python virtual environment:
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### 3. Run the Vue.js Frontend
Open a new terminal window, navigate into the `frontend` directory:
```bash
cd frontend
npm install
npm run dev
```

## 📝 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
