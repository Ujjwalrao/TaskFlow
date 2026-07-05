# TaskFlow — Personal Productivity OS

A free, self-hosted productivity platform: tasks, recurring habits with streaks,
goals, no-login team collaboration, local semantic search, PDF/CSV reporting,
a feedback loop for smarter suggestions, and free Telegram notifications.

**No sign-up. No login. No paid API required.**

---

## Features

- **Tasks** — priorities, due dates, recurring rules (daily / weekly / monthly)
- **Habits** — daily/weekly tracking with automatic streak calculation
- **Goals** — linked to tasks, auto-computed progress
- **Team** — add teammates by name only (no accounts/passwords), see per-person
  completion analytics
- **Semantic Search** — finds tasks/goals/habits/documents by meaning, not just
  keywords, using a local embedding model (`all-MiniLM-L6-v2`). Runs entirely
  on your machine — no API key, no per-query cost.
- **Reports** — one-click weekly PDF report and CSV export, generated locally
- **Feedback loop** — every AI suggestion you accept/reject is logged, building
  a simple, transparent acceptance-rate score per suggestion type
- **Notifications** — free Telegram bot integration
- **Dark mode** — toggle in the top bar, defaults to a clean light/white theme
- **Offline support** — installable PWA with a basic service worker cache

### Not wired up yet (need your own credentials)
Outlook Calendar, Notion, Slack, and Jira integrations all require an OAuth
app registered under **your own account** with that provider — the same
pattern as Google Calendar below.

### Google Calendar — two-way sync (available now)
1. Go to [Google Cloud Console](https://console.cloud.google.com) → create a project
2. Enable the **Google Calendar API**
3. Create an **OAuth client ID** (Web application), with redirect URI:
   `http://localhost:5000/api/integrations/google/callback`
4. Copy the Client ID and Client Secret into `backend/.env`:
   ```
   GOOGLE_CLIENT_ID=your-client-id
   GOOGLE_CLIENT_SECRET=your-client-secret
   ```
5. Restart the backend, go to Settings in the app, click "Connect Google Calendar"

---

## Tech Stack

- **Frontend**: React 18, Vite, TailwindCSS, React Router
- **Backend**: Python, Flask, SQLite (zero-config, no external DB signup)
- **AI**: `sentence-transformers` (local embeddings — the only "ML" in this
  app is a real vector model, not a wrapped LLM API call)
- **PDF/CSV**: reportlab, Python's csv module
- **Notifications**: Telegram Bot API (free)

---

## Setup

### Backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python app.py
```
Runs on `http://localhost:5000`. The database (`taskflow.db`) and a default
local workspace member ("You") are created automatically on first run.

### Frontend
```bash
cd frontend
npm install
npm run dev
```
Runs on `http://localhost:5173` and proxies `/api` calls to the backend.

---

### Database — SQLite (dev) or Postgres/Neon (production)
By default the app uses zero-config SQLite (`backend/taskflow.db`) — perfect
for local development. For production, set `DATABASE_URL` and it
automatically switches to Postgres, no code changes needed:

1. [neon.tech](https://neon.tech) → free account → "New Project"
2. Copy the connection string it gives you
3. Add to `backend/.env`:
   ```
   DATABASE_URL=postgresql://user:password@host/dbname
   ```

**Why this matters for deployment**: Render's free web service tier does not
persist local disk storage between deploys/restarts — plain SQLite there
would lose all data periodically. Postgres via Neon's free tier solves this
with zero cost.

## Deployment (free tiers)

### Backend — Render
1. Push this repo to GitHub
2. New Web Service on Render → connect the repo → root directory `backend`
3. Build command: `pip install -r requirements.txt`
4. Start command: `gunicorn wsgi:app --bind 0.0.0.0:$PORT --timeout 120`
5. Add `DATABASE_URL` (from Neon) plus any integration keys as environment
   variables (Settings → Environment)
6. A ready-made `render.yaml` is included in the repo root — Render can also
   auto-detect it via "New → Blueprint"

### Frontend — Vercel
1. Import the repo → root directory `frontend` → framework preset `Vite`
2. A ready-made `vercel.json` is included; update the `rewrites` destination
   in it to your actual Render backend URL before deploying

---

## Folder Structure

```text
taskflow/
├── backend/
│   ├── app.py
│   ├── database/       # SQLite setup, zero-config
│   ├── routes/         # API endpoints per feature
│   ├── services/       # Recurrence engine, embeddings, export, etc.
│   └── requirements.txt
└── frontend/
    ├── src/
    │   ├── pages/       # Dashboard, Tasks, Habits, Goals, Team, Search, Reports, Settings
    │   ├── components/  # Sidebar, Topbar (incl. dark mode toggle)
    │   ├── context/      # Theme context
    │   └── lib/          # API client
    └── package.json
```
