# Wealth Tracker

A comprehensive full-stack Financial Tracker application built with Python, Django REST Framework, MySQL, and Vue.js.

This application allows you to track:
1. **Budgeting**: Income, Expenses, and spending weight breakdown.
2. **Investments**: Monthly portfolio snapshots, profit tracking, and asset allocation.
3. **Liabilities**: Loan tracking, debt reduction, and remaining principal balances.

## 🚀 Homelab Deployment (Recommended)

Wealth Tracker is built for containerized environments. It automatically builds and pushes Docker images to GitHub Container Registry (GHCR) using GitHub Actions.

### Option A: Docker Compose (Easiest)

If you are running Docker on your homelab (e.g., Ubuntu VM, Proxmox LXC), you can deploy the entire stack with a single command.

1. Clone the repository:
   ```bash
   git clone https://github.com/FikriNasarudin/wealth-tracker.git
   cd wealth-tracker
   ```
2. *(Optional)* If you want to use the pre-built GHCR images instead of building locally, edit the `docker-compose.yml` to uncomment the `image: ghcr.io/...` lines and comment the `build:` lines.
3. Start the services in detached mode:
   ```bash
   docker compose up -d
   ```
4. **Migrate the Database**: Since it's the first run, initialize the Django tables:
   ```bash
   docker compose exec backend python manage.py migrate
   ```
5. Access the application in your browser at `http://<your-server-ip>/`.

### Option B: Kubernetes (K3s, Minikube, Proxmox)

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
4. Add `wealthtracker.local` to your local machine's `/etc/hosts` pointing to your cluster IP.
5. Initialize the database by getting the backend pod name:
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
The backend API will run at `http://127.0.0.1:8000/`.

### 3. Run the Vue.js Frontend
Open a new terminal window, navigate into the `frontend` directory:
```bash
cd frontend
npm install
npm run dev
```
The frontend application will run at `http://localhost:5173/`. 

## 📝 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
