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
