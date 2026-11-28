# Jugnu

A mentorship app for students in India. A student chats with a career guide, gets a direction and a
roadmap, connects with a mentor, books a session and talks with others in the community.

- `backend/`: FastAPI, PostgreSQL, Alembic, Pydantic
- `frontend/`: React, Vite, TypeScript
- `resources/`: the original design and chatbot prototypes (reference only)

More: [architecture.md](architecture.md) · [learning.md](learning.md) · [CLAUDE.md](CLAUDE.md)

## Run it

You need Python 3.12, Node 22 or newer, and PostgreSQL 16 running. Commands are for PowerShell.

**1. Backend**

```powershell
cd backend
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements-dev.txt
copy .env.example .env
```

Edit `backend/.env`. Set `DB_PASSWORD`. To try everything without Google or an AI key, also set:

```
DEMO_LOGIN=true
DEMO_JWT_SECRET=<output of: python -c "import secrets; print(secrets.token_urlsafe(48))">
AI_MODE=demo
```

Then create the databases, tables and sample people, and start the API:

```powershell
.venv\Scripts\python -m scripts.create_db
.venv\Scripts\alembic upgrade head
.venv\Scripts\python -m scripts.seed
.venv\Scripts\python -m uvicorn app.main:app --reload
```

API documentation: http://127.0.0.1:8000/api/docs

**2. Frontend** (second terminal)

```powershell
cd frontend
npm install
npm run dev
```

Open **http://localhost:5173**. Use `localhost`, not `127.0.0.1`: it is the address registered for Google login.

## Set up Google login (Supabase)

Supabase is used for login only. App data stays in your own PostgreSQL.

1. Create a project at supabase.com. Under **JWT signing keys**, use an asymmetric key (ES256). A project
   still on the legacy shared secret must switch, otherwise every login is rejected.
2. In Supabase, open **Authentication > Providers > Google** and copy the callback URL shown there.
3. In Google Cloud, create an **OAuth client ID** of type *Web application*:
   - Authorized JavaScript origin: `http://localhost:5173`
   - Authorized redirect URI: the callback URL from step 2
   - Scopes: `openid`, `userinfo.email`, `userinfo.profile`
4. Paste the Google client ID and client secret into Supabase's Google provider page and enable it.
5. In Supabase **URL Configuration**, set the Site URL to `http://localhost:5173` and add
   `http://localhost:5173/auth/callback` to the redirect URLs.
6. In `backend/.env`, set `SUPABASE_URL` and `SUPABASE_PUBLISHABLE_KEY` (starts with `sb_publishable_`).
   Never use a secret key here: this value is sent to the browser. Restart the API.

## Use the real AI guide

Set `AI_MODE=openrouter` and `OPENROUTER_API_KEY` in `backend/.env`. One full intake is roughly 25 AI calls.
Free models have daily limits, so rehearse in demo mode.

## Deploy on Vercel

One Vercel project serves both parts: `vercel.json` sends `/api/*` to FastAPI and everything else to the React
build. The database lives on Neon (free PostgreSQL). Details: [architecture.md](architecture.md#hosting-on-vercel).
Full walkthrough with checks and troubleshooting: [DEPLOY-VERCEL.txt](DEPLOY-VERCEL.txt).

1. **Database.** Create a project at neon.com. From its connection details note the host, user, password and
   database name. Neon shows two hosts: the **pooled** one (contains `-pooler`) is for the app, the direct one for
   migrations.
2. **Tables and sample people.** On your computer, temporarily point `backend/.env` at Neon (the direct host) with
   `DB_SSLMODE=require`, then run from `backend/`:
   ```powershell
   .venv\Scripts\alembic upgrade head
   .venv\Scripts\python -m scripts.seed
   ```
   Skip `scripts.create_db`; Neon already created the database. Point `.env` back at your local database after.
3. **Vercel project.** At vercel.com, import the GitHub repository and keep the root directory as the repository
   root (it reads `vercel.json`). Add these environment variables, then deploy:

   | Variable | Value |
   |---|---|
   | `DB_HOST` | Neon's **pooled** host |
   | `DB_PORT` `DB_USER` `DB_PASSWORD` `DB_NAME` | From Neon (port is usually 5432) |
   | `DB_SSLMODE` | `require` |
   | `SUPABASE_URL` `SUPABASE_PUBLISHABLE_KEY` | As for local Google login |
   | `AI_MODE` | `openrouter` (with `OPENROUTER_API_KEY`) or `demo` |
   | `DEMO_LOGIN` | `false`. Set `true` (with `DEMO_JWT_SECRET`) only for a judged demo with sample data: anyone with the link can then log in as the sample people |

4. **Login addresses.** With your address `https://<project>.vercel.app`:
   - Supabase, **URL Configuration**: set it as the Site URL and add `https://<project>.vercel.app/auth/callback`
     to the redirect URLs.
   - Google Cloud OAuth client: add it to the Authorized JavaScript origins.
5. **Check it.** `https://<project>.vercel.app/api/health` shows `{"status":"ok"}`. Open the site, reload a page
   such as `/mentors`, and log in with Google.

There is no rate limiting: anyone who logs in uses your OpenRouter allowance.

## Useful commands (from `backend/`)

| Task | Command |
|---|---|
| Run tests | `.venv\Scripts\python -m pytest` |
| Reset the demo users before a presentation | `.venv\Scripts\python -m scripts.seed --reset-demo` |
| List and approve new mentors | `.venv\Scripts\python -m scripts.approve_mentor [id]` |
| List students flagged for a human to check on | `.venv\Scripts\python -m scripts.list_followups` |
| Create a migration after changing models | `.venv\Scripts\alembic revision --autogenerate -m "what changed"` |

## Demo in two tabs

Demo logins are per tab, so a student and a mentor can be open side by side.

1. Tab 1: log in as **Student finishing the guide**, open the guide and answer "yes".
2. Open Ananya Rao's profile and book a session.
3. Tab 2: log in as **Mentor**, confirm the session and send a message. It appears in tab 1 within seconds.

Sample people and demo login are for development only. Do not use them on a public server.
