# Cloud Deployment Guide (100% Free Tier)

Step-by-step guide to deploying the **Real-Time Cybersecurity Threat Monitoring & Incident Response System** to the cloud so that it can be accessed from any laptop, mobile phone, or external virtual machine via HTTPS.

---

## Architecture Overview
- **Database:** Cloud PostgreSQL (Free on Render or Neon.tech / Supabase)
- **Backend:** Flask REST API with Gunicorn (Free on Render or Railway)
- **Frontend:** React.js Vite Dashboard (Free on Vercel or Netlify)
- **Monitoring Agent:** Runs on any external Windows/Linux laptop or VM

---

## 🚀 STEP 1: Deploy PostgreSQL & Backend to Render (Free)

### 1. Push Code to GitHub
1. Create a new GitHub repository: `cyber-threat-monitoring-system`.
2. Push this repository to GitHub:
   ```bash
   git init
   git add .
   git commit -m "Initial commit of Cyber SOC project"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/cyber-threat-monitoring-system.git
   git push -u origin main
   ```

### 2. Deploy Database on Render
1. Go to [render.com](https://render.com) and sign in with GitHub.
2. Click **New +** → **PostgreSQL**.
3. Name it: `cyber-soc-postgres`.
4. Region: Choose the closest region (e.g., Oregon or Frankfurt).
5. Plan: Select **Free**.
6. Click **Create Database**.
7. Once created, copy the **Internal Database URL** (or External Connection String).

### 3. Deploy Backend Web Service on Render
1. Click **New +** → **Web Service**.
2. Select your GitHub repository.
3. Configure settings:
   - **Name:** `cyber-soc-backend`
   - **Root Directory:** `backend`
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn --bind 0.0.0.0:$PORT --workers 3 --timeout 120 app:app`
   - **Plan:** Free
4. Add **Environment Variables**:
   - `DATABASE_URL` = [Paste your PostgreSQL Connection String from Step 2]
   - `API_SECRET` = `cyber-soc-super-secret-key-prod-2026`
   - `JWT_SECRET` = `jwt-defense-guard-token-secret-prod-2026`
   - `CORS_ORIGINS` = `*`
   - `FLASK_ENV` = `production`
5. Click **Create Web Service**.
6. Wait 2–3 minutes until the service is live. Your live backend URL will look like:
   `https://cyber-soc-backend.onrender.com`
7. Test it: Open `https://cyber-soc-backend.onrender.com/api/health` in your browser. You should see `{"status": "online"}`.
8. Interactive Swagger Docs: Open `https://cyber-soc-backend.onrender.com/api/docs`.

---

## 🌐 STEP 2: Deploy Frontend to Vercel (Free)

1. Go to [vercel.com](https://vercel.com) and log in with GitHub.
2. Click **Add New...** → **Project**.
3. Import your GitHub repository `cyber-threat-monitoring-system`.
4. Configure Project:
   - **Root Directory:** Edit to select `frontend`
   - **Framework Preset:** `Vite`
5. Add **Environment Variable**:
   - `VITE_API_URL` = `https://cyber-soc-backend.onrender.com` (Your Render backend URL)
6. Click **Deploy**.
7. In ~60 seconds, your live frontend URL will be ready:
   `https://cyber-soc-frontend.vercel.app`
8. Open this URL on your phone or any external computer. You can log in with:
   - **Username:** `admin`
   - **Password:** `AdminSecure2026!`

---

## 💻 STEP 3: Connect External Laptop / VM Security Agent

On your second laptop, virtual machine, or teammate's computer:

1. Clone or copy the `security-agent` folder to the second laptop.
2. Install requirements:
   ```bash
   cd security-agent
   pip install -r requirements.txt
   ```
3. Set the live server environment variables:
   - **Windows (PowerShell):**
     ```powershell
     $env:SERVER_URL = "https://cyber-soc-backend.onrender.com"
     $env:DEVICE_ID = "SECOND-LAPTOP-STUDENT"
     $env:DEVICE_TOKEN = "sec_dev_token_alpha_9921"
     ```
   - **Linux / Mac (Terminal):**
     ```bash
     export SERVER_URL="https://cyber-soc-backend.onrender.com"
     export DEVICE_ID="SECOND-LAPTOP-STUDENT"
     export DEVICE_TOKEN="sec_dev_token_alpha_9921"
     ```
4. Run the continuous agent daemon:
   ```bash
   python agent.py
   ```
   Notice that the device immediately appears **ONLINE** on your live Vercel dashboard!

5. Run the safe demonstration script to trigger alerts:
   ```bash
   python simulate_events.py
   ```
   Select Option `1` (Brute Force) or Option `5` (Full Suite).
   Instantly look at the Vercel dashboard on your main screen—the alerts will flash live!

---

## 🔒 Security Hardening Verification Checklist
- [x] Passwords salted with PBKDF2; plaintext passwords never stored.
- [x] JWT tokens verified on every protected route.
- [x] Device API keys verified on every ingestion request.
- [x] All database operations execute through parameterized SQLAlchemy queries.
- [x] Security headers (`X-Content-Type-Options`, `X-Frame-Options`, `Strict-Transport-Security`) injected on all responses.
