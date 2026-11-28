# Jugnu: project guide

Student mentorship app for a hackathon. React frontend, FastAPI backend, PostgreSQL. Google login through
Supabase Auth. Two chatbots: intake (career guide) and helper (dashboard).

- Design, schema, API map, decisions: [architecture.md](architecture.md)
- Study guide and lessons log: [learning.md](learning.md)
- Setup for people: [README.md](README.md)
- Deploying: [DEPLOY-VERCEL.txt](DEPLOY-VERCEL.txt)

## Keep the docs true

With every relevant change, in the same piece of work:
- `architecture.md`: schema, endpoints, login, chatbot flow, configuration or a design decision changed
- `learning.md`: add a dated entry to the lessons log for a bug, surprise or decision worth remembering
- this file: commands, folders, conventions or rules changed
- `DEPLOY-VERCEL.txt`: hosting, settings or the deploy steps changed

No secrets or personal details in any of them.

## Folders

| Path | What |
|---|---|
| `backend/app/models/` | SQLAlchemy tables |
| `backend/app/schemas/` | Pydantic request and response models |
| `backend/app/routers/` | HTTP endpoints, thin |
| `backend/app/services/` | Business rules: bookings, requests, mentors, helper |
| `backend/app/services/intake/` | Intake chatbot: `engine` (state machine), `store` (database), `llm`, `scripted` (demo) |
| `backend/app/domain/` | Career fields, roadmaps, demo ids |
| `backend/app/security.py`, `deps.py` | Token verification, current user, role checks |
| `backend/scripts/` | `create_db`, `seed`, `approve_mentor`, `list_followups` |
| `frontend/src/api/` | `client` (fetch), `hooks` (React Query), `types` (mirror of the schemas) |
| `frontend/src/auth/` | Supabase client, login state, route guard |
| `frontend/src/pages/`, `components/` | Screens and shared parts |
| `resources/` | Prototypes. Read only: never edit |
| `vercel.json`, `.vercelignore` | Hosting: `/api/*` goes to `backend/`, the rest to the `frontend/` build. Keep every endpoint under `/api` |

## Commands

From `backend/` (PowerShell):

```
.venv\Scripts\python -m uvicorn app.main:app --reload
.venv\Scripts\python -m pytest
.venv\Scripts\alembic upgrade head
.venv\Scripts\alembic revision --autogenerate -m "message"
.venv\Scripts\alembic check
.venv\Scripts\python -m scripts.seed --reset-demo
```

From `frontend/`: `npm run dev`, `npm run build` (type-checks first).

Tests need PostgreSQL. They use the `jugnu_test` database, empty it before each test, and refuse any database
whose name does not end in `_test`.

## Environment variables (`backend/.env`, template in `.env.example`)

`DB_HOST` `DB_PORT` `DB_USER` `DB_PASSWORD` `DB_NAME` `DB_SSLMODE` (`require` for hosted databases) · `SUPABASE_URL` `SUPABASE_PUBLISHABLE_KEY` ·
`DEMO_LOGIN` `DEMO_JWT_SECRET` · `AI_MODE` (`openrouter` or `demo`) `OPENROUTER_API_KEY`
`INTAKE_CHAT_MODEL` `INTAKE_EXTRACT_MODEL`

The frontend has no settings of its own. It reads public ones from `GET /api/config`.

## Conventions

- Endpoints are plain `def` (synchronous SQLAlchemy). Do not mix in async database code.
- Request models extend `In` (unknown keys rejected); responses extend `Out`. Errors use
  `ApiError(status, code, message)`; the frontend acts on `code`.
- Money is an integer number of paise. Rates are whole rupees.
- Career field keys live only in `domain/fields.py`. The key is `defense`; the label is "Defence".
- Every schema change is an Alembic migration. Alembic does not detect changed CHECK constraints: write
  those by hand. Avoid `%` in constraints (it gets doubled); use `mod()`.
- When `schemas/api.py` changes, update `frontend/src/api/types.ts`.
- `styles/style.css` is the prototype's file, unchanged. Put new rules in `additions.css`. Keep the HTML
  nesting: some selectors depend on position.

## Rules that must not be broken

**Login and permissions**
- Identity is the verified token's `sub`, stored as `users.auth_subject`. Never match accounts by email.
- Role comes from our database only, never from token metadata (users can edit it).
- Accepted Supabase algorithms are ES256 and RS256 only. Demo tokens have their own issuer and secret.
- `DEMO_LOGIN` stays off by default. No Supabase secret key anywhere in this project.
- The server checks every permission. `RequireAuth` in React is convenience only.
- A conversation is visible only to its two people and only once accepted. Others get 404.

**Money**
- The server computes prices. Check the idempotency key before the rate. Payments are simulated.

**Chatbots**
- Never hold a database connection during an AI call: chat endpoints do not use `DbDep`.
- Take the lease (`store.acquire`) before building `IntakeSession`; release it in `finally`.
- `needs_human_followup`, `mentor_focus` and `reasoning` never reach students or the helper prompt.
- Never fall back to the scripted guide silently. The UI must label it "Demo guide".
- The support, AI and privacy notices stay visible in the chats.

**People's safety and privacy**
- Students may be minors. New mentors are hidden until approved by a person.
- Show chat and user text as text. No `dangerouslySetInnerHTML`.
- `resources/` holds a saved chat in a database file and a zip. Never commit those files.

## Not built

Dockerfiles (the app is prepared for them), real payments, scheduling, file uploads, rate limiting.
