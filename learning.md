# Learning

Part 1 explains the ideas this project uses, with where to see them. Part 2 is a dated log of problems and decisions.

## Part 1: Study guide

### FastAPI: endpoints and dependencies
A function plus a decorator becomes an endpoint. Dependencies run first and hand it what it needs:

```python
@router.patch("/mentor/rate")
def update_rate(data: RateIn, user: MentorDep, db: DbDep) -> OwnMentorOut:
```

`MentorDep` means: read the token, verify it, find the user, refuse anyone who is not a mentor. The endpoint cannot
run without that. See `backend/app/deps.py`.

### Pydantic: never trust input
Every request body is checked before our code sees it. `RateIn` accepts only an integer from 1 to 100,000. `In` sets
`extra="forbid"`, so a student cannot sneak `total_paise` into a booking. Response models work the other way: they
decide exactly which fields leave the server. See `backend/app/schemas/`.

### SQLAlchemy and PostgreSQL: let the database say no
Models describe tables. Constraints are the last line of defence: even buggy code cannot save a booking whose total
is wrong. `UNIQUE(student_id, mentor_id)` with `ON CONFLICT DO NOTHING` makes "request a mentor" safe to repeat.
See `backend/app/models/mentorship.py`.

### Transactions and locks
`confirm_booking` locks the booking (`FOR UPDATE`), opens the conversation and marks it confirmed in one transaction.
Either all of it happens or none. `create_booking` reads the mentor `FOR SHARE`, so the rate cannot change between
checking and saving. See `backend/app/services/bookings.py`.

### Alembic: version control for tables
Change a model, then `alembic revision --autogenerate`. Always read the result: it can miss things. `upgrade head`
applies it, `downgrade` undoes it, `alembic check` tells you whether models and migrations agree.

### JWT and JWKS: proving who you are
A JWT is a signed note: "this is user X, until 5 pm". Supabase signs it with a private key; we verify it with the
public key from its JWKS address. Verifying means more than the signature: also issuer, audience, expiry and
algorithm. Never let the token choose its own algorithm. See `backend/app/security.py`.

### OAuth with PKCE: logging in with Google
The browser invents a secret (verifier) and sends only its hash (challenge) when login starts. Google returns a code.
The code is useless without the verifier, so stealing it from the URL does not help. See `frontend/src/auth/`.

### Idempotency: pressing Pay twice
The browser makes one random key per checkout. The server stores it with the booking, unique per student. A repeat
finds the existing booking instead of creating another. See `frontend/src/pages/Book.tsx`.

### React Query: server data in React
`useQuery` fetches, caches and refreshes. After a change, we invalidate the affected queries and they refetch.
Polling is one option: `refetchInterval`. See `frontend/src/api/hooks.ts`.

### A chatbot as a state machine
The AI writes the words; our code decides what happens. Facts are extracted as JSON and merged by rules, missing
topics are listed for the next question, and limits guarantee the chat ends. The AI's output is treated as untrusted:
an unknown field becomes `undecided`. See `backend/app/services/intake/engine.py`.

### Leases: one turn at a time
An AI call takes seconds. A database lock would hold a connection that whole time. A lease is a note in the row: "busy
until 12:02". Claiming it is one atomic `UPDATE`, and it expires by itself after a crash. See `store.acquire`.

### Questions judges may ask
- *Can a student read someone else's chat?* No. Every query uses the id from the verified token. Tests cover it.
- *Can someone change the price in the browser?* No. The server computes it; the client's figure is only compared.
- *What if the AI is down?* Replies fail visibly and can be retried. After three routing failures the student is sent
  to the dashboard as undecided, with a note for a mentor. The rest of the app keeps working.
- *Is payment real?* No. It is simulated and labelled as a test.

## Part 2: Lessons log

Newest first. Add: what happened, why, what we did.

### 2026-11-25: first build
- **A student could get stuck forever.** The prototype counted routing failures in memory, but a website rebuilds the
  session for every request, so the count never reached three. Now stored in the database.
- **A summary nobody saw could be "confirmed".** If the summary failed to send and the student's next message looked
  like a yes, the chat would finish. Now only a delivered summary can be confirmed.
- **Retrying used up turns.** A resent message was stored again and counted toward the 20-message limit. Fixed.
- **The greeting could appear twice.** React StrictMode runs effects twice in development. The server now creates the
  chat with `ON CONFLICT DO NOTHING`, so calling start twice is harmless.
- **The same StrictMode behaviour broke "return to the page you wanted".** Reading and clearing the saved page in one
  step lost it on the second run. Reading and clearing are now separate.
- **Alembic doubled a `%`.** A constraint with `% 100` came out as `%% 100` in the migration. Use `mod()`.
- **Tests that passed for the wrong reason.** `tests/__init__.py` made pytest load `conftest.py` twice, with two
  signing keys. Every token was rejected, so the "bad token" tests passed without testing anything. The valid-token
  tests failing gave it away. Always test that the good case works, and break the code on purpose to see tests fail.
- **JSON null is not SQL NULL.** Saving without an analysis would have overwritten the old one with JSON `null`.
  `JSONB(none_as_null=True)` fixes it.
- **Enter in Hindi and Bengali keyboards.** Enter also picks a word while typing. Check `isComposing` before sending.
- **Supabase keys changed.** Use `sb_publishable_` keys and asymmetric signing keys; the older `anon` key is being
  retired at the end of 2026.
- **A bug in the prototype's login we did not copy.** Anyone could sign up as an existing mentor and read their inbox.

### 2026-11-28: getting ready for Vercel

- **Check the host's time limits against your slowest request.** Netlify's proxy stops after 26 seconds. A guide
  turn can take about 75 seconds, so it would have failed only on slow AI days, which is the worst kind of bug.
  Vercel runs the backend itself and allows 300 seconds.
- **Connection poolers and prepared statements.** psycopg switches a query to a server-side prepared statement
  after five runs. Behind a pooler in transaction mode, the next request may land on a different database
  connection that never saw it. `prepare_threshold=None` turns this off. We confirmed it: with the default the
  database listed one prepared statement after ten runs, with the setting none.
- **`vercel deploy` uploads your folder, not git.** `.gitignore` does not protect `backend/.env` there;
  `.vercelignore` does.
