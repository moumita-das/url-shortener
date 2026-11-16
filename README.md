# URL Shortener

> ...because size matters.

A full-stack URL shortener: paste a long link, get a short one back; paste the
short one, get the original. Built with **FastAPI + MongoDB** on the backend and
**React + Vite** on the frontend, with a seesaw as the UI metaphor — the two
inputs sit on opposite ends of a tilting beam, and the beam leans toward
whichever direction you're translating.

---

## What makes it interesting

Most toy shorteners hash the long URL or increment a counter. Both leak
information: a hash collides, and a counter makes every link guessable from the
one before it. This project instead **pre-generates a pool of unused IDs and
hands them out at random**.

A window of consecutive integers (starting at 10⁹, so every alias is at least
six characters) is reserved into an `unused_ids` collection. On each request the
generator samples a handful at random, claims one with an atomic
`find_one_and_delete`, and moves it to `used_ids`. When the pool runs low it
reserves the next window.

The claimed integer is then rendered in **base58** — the Bitcoin alphabet, which
drops `0`, `O`, `I` and `l` so an alias can be read aloud or copied off a screen
without ambiguity:

```
1000000000  ->  2XNGAK
```

Custom aliases run the same machinery backwards: the alias is decoded to its
integer, and registering it is simply a matter of claiming that integer in
`used_ids`. One namespace, one source of truth, no separate collision check.

---

## Stack

| Layer | Built with |
|---|---|
| API | FastAPI, Uvicorn |
| Database | MongoDB Atlas (via PyMongo) |
| Auth | JWT (PyJWT) + Argon2 password hashing (pwdlib) |
| Config | pydantic-settings, `.env`-backed |
| Frontend | React 19, Vite, React Router, react-bootstrap |
| HTTP | Axios, with interceptors for token injection and 401 handling |

---

## API

| Method | Endpoint | Auth | Purpose |
|---|---|---|---|
| `POST` | `/register_user` | — | Create an account (JSON body) |
| `POST` | `/login` | — | Exchange credentials for a JWT (form-encoded) |
| `GET` | `/generate_url` | ✅ | Shorten a URL, optionally with a custom alias |
| `GET` | `/get_long_url` | — | Resolve a short URL back to the original |
| `DELETE` | `/delete_url` | ✅ | Delete a mapping you own |

`/generate_url` is idempotent: if the long URL has been shortened before it
returns the existing alias rather than minting a second one.

Interactive docs are at `http://localhost:8000/docs` once the server is running.

---

## Running it

### Prerequisites

- Python 3.13
- Node 20+
- A MongoDB connection string (Atlas or local)

### Backend

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows;  source .venv/bin/activate elsewhere
pip install -r backend/requirements.txt
```

Create `backend/.env`:

```ini
MONGODB_USERNAME=...
MONGODB_PASSWORD=...
MONGODB_HOST=cluster0.xxxxx.mongodb.net
MONGODB_NAME=url_shortener
DOMAIN_NAME=http://localhost:8000/
COUNTER_WINDOW_LENGTH=10
SECRET_KEY=...                  # python -c "import secrets; print(secrets.token_hex(32))"
ALGORITHM=HS256
```

Then, from the `backend/` directory:

```bash
python -m server.main
```

The server listens on `http://0.0.0.0:8000`. A VS Code debug configuration is
checked in at [.vscode/launch.json](.vscode/launch.json).

### Frontend

Create `frontend/.env.local`:

```ini
VITE_API_URL=http://localhost:8000
```

Only `VITE_`-prefixed variables reach client code, and Vite inlines them at
startup — restart the dev server after changing them.

```bash
cd frontend
npm install
npm run dev
```

---

## Layout

```
url-shortener/
├── backend/
│   ├── db/               # MongoDB client
│   ├── id_generator/     # base58 encoding + the unused-ID pool
│   ├── server/
│   │   ├── main.py       # FastAPI app and routes
│   │   ├── crud.py       # collection access
│   │   └── security.py   # JWT issuing, password hashing
│   └── settings.py       # pydantic-settings, reads backend/.env
└── frontend/
    └── src/
        ├── api.js        # axios instance + interceptors
        ├── auth.jsx      # auth context
        ├── components/   # layout and navbar
        └── pages/        # Home (the seesaw), Login
```

---

## Status

A learning project, not production software. Known rough edges are tracked
separately — notably that short URLs are stored with the domain baked in (so
lookups need the full URL, not the bare alias), and that CORS is currently wide
open for local development.
