# Frontend — Wealth Tracker

This is the Vue.js frontend for the Wealth Tracker application. It communicates with the [Django REST API backend](../backend/README.md) to display budgets, investments, liabilities, and insights.

## 🧰 Tech Stack

- **Framework**: [Vue.js 3](https://vuejs.org/) with Vite
- **Styling**: CSS / Component-scoped styles
- **Auth**: Google OAuth 2.0 (optional)
- **Build**: Served via NGINX in production (Docker)

---

## 🛠️ Local Development

> Make sure the backend API is running before starting the frontend.
> See [backend/README.md](../backend/README.md) for backend setup instructions.

### 1. Install Dependencies
Navigate into the `frontend` directory and install packages:
```bash
cd frontend
npm install
```

### 2. Configure Environment
The frontend uses Vite environment variables. By default it points to the backend at `http://localhost:8000`. If your backend runs on a different port, create a `.env.local` file:
```env
VITE_API_BASE_URL=http://localhost:8000
VITE_GOOGLE_CLIENT_ID=your-google-client-id   # optional
```

### 3. Start the Dev Server
```bash
npm run dev
```

The app will be available at `http://localhost:5173` (or the port Vite picks).

### 4. Build for Production
```bash
npm run build
```

The compiled output will be placed in the `dist/` directory, which is served by NGINX when running via Docker.

---

## 🐳 Docker

The frontend is containerized using a multi-stage Dockerfile:
- **Stage 1** — `node` image builds the Vite project
- **Stage 2** — `nginx` image serves the `dist/` output

To build and run the frontend container in isolation:
```bash
docker build -t wealth-tracker-frontend ./frontend
docker run -p 80:80 wealth-tracker-frontend
```

Or just use Docker Compose from the project root (recommended):
```bash
docker compose up -d --build frontend
```
