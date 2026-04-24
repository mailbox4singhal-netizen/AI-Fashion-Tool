# AI Fashion Intelligence & Design Platform

Full-stack implementation of the SRS/FRS — FastAPI backend + React frontend with
pink/violet/neon-green glassmorphism aesthetic and Aptos typography.

---

## ⚡ TL;DR — plug in your API key and go

```bash
cd backend
cp .env.example .env
# edit .env — paste your key into ANTHROPIC_API_KEY (or OPENAI_API_KEY)
cd ..
./start.sh
```

Open <http://localhost:5173>. You'll land on the login page. Sign in with a demo
account (pill buttons on the form) or register a new one.

---

## 🔐 Login-first with role-based access

**The entry point is the login page — not a public landing page.** Unauthenticated
users visiting any URL get redirected to `/login`. After successful sign-in, users
are routed to a destination their role permits.

### Three roles, three experiences

| Role       | Lands on    | Can access                                           | Seeded account                         |
| ---------- | ----------- | ---------------------------------------------------- | -------------------------------------- |
| `designer` | `/designer` | Designer workspace, results, history                 | `demo@fashion.ai` / `demo1234`         |
| `shopper`  | `/browse`   | Trend browser only (read-only consumer view)         | `shopper@fashion.ai` / `shopper1234`   |
| `admin`    | `/designer` | **Everything** — workspace, history, admin dashboard | `admin@fashion.ai` / `admin1234`       |

### How the guard works

Route protection lives in `frontend/src/App.jsx`:

```jsx
<Route path="/admin" element={
  <Protected roles={['admin']}><Admin /></Protected>
} />
<Route path="/designer" element={
  <Protected roles={['designer', 'admin']}><Designer /></Protected>
} />
```

The `<Protected>` component:

1. Redirects unauthenticated users to `/login` (remembering where they came from)
2. Redirects authenticated users with the wrong role back to their role's home
3. Lets matching users through

The backend mirrors this with the `require_admin` dependency on sensitive
routes (`/admin/*`) in `backend/app/routes/admin.py`.

---

## 🧠 Integrating your API key

The platform ships with a **3-provider LLM client** (`backend/app/services/llm_client.py`).
Set one env var to choose — everything else auto-configures.

### Step 1 — Copy the template

```bash
cd backend
cp .env.example .env
```

### Step 2 — Pick a provider and paste your key

**For Anthropic (Claude) — recommended:**

```env
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-api03-YOUR_KEY_HERE
ANTHROPIC_MODEL=claude-haiku-4-5-20251001
```

**For OpenAI:**

```env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-YOUR_KEY_HERE
OPENAI_MODEL=gpt-4o-mini
```

**For offline / zero-key demo:**

```env
LLM_PROVIDER=mock
```

### Step 3 — Run

```bash
./start.sh
```

That's it. The four AI services (trend, color, design, tech pack) automatically
route through your configured provider. If a call fails, they fall back to
deterministic mock output so the demo never breaks mid-presentation.

### Verify your key is wired up

With the server running:

```bash
curl http://localhost:8000/ai-status
```

You'll see:

```json
{
  "provider": "anthropic",
  "model": "claude-haiku-4-5-20251001",
  "llm_enabled": true
}
```

If `llm_enabled` is `false`, your key isn't being read — double-check `.env` is
in the `backend/` folder and the variable name matches exactly.

### How the services use it

Every AI service follows the same try-LLM-else-mock pattern:

```python
# backend/app/services/trend_service.py
async def get_trends(data):
    if not llm_enabled():
        return _mock(data)
    try:
        return await get_llm_client().complete_json(
            system=TREND_SYSTEM,
            user=trend_user(data),
        )
    except Exception as e:
        log_event("trend_service.llm_failed_fallback_to_mock", error=str(e))
        return _mock(data)
```

All prompts live in `backend/app/utils/prompts.py` — versioned (V1.2.0, V1.1.3,
V1.3.0, V1.0.4) per SRS §5.5 and FRS §8. Every LLM call is written to the
`audit_logs` table with prompt version + model version for compliance (FRS F10).

### Swapping in a different provider

Add a new provider class to `llm_client.py` that implements
`async def complete(self, system, user) -> str`. Wire it up in `LLMClient.__init__`.
Zero changes needed anywhere else.

---

## 🏃 Running the app

### One-shot

```bash
chmod +x start.sh
./start.sh
```

Boots backend on `:8000` and frontend on `:5173`.

### Manual (two terminals)

**Backend:**

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
# Swagger UI: http://localhost:8000/docs
```

**Frontend:**

```bash
cd frontend
npm install
npm run dev
# http://localhost:5173
```

---

## 📂 Project layout

```
ai-fashion-platform/
├── backend/                              FastAPI service
│   ├── app/
│   │   ├── main.py                       Entry + route wiring + lifespan seed
│   │   ├── config.py                     Settings (reads .env automatically)
│   │   ├── database.py                   SQLAlchemy engine + session
│   │   ├── auth.py                       JWT + bcrypt utilities
│   │   ├── schemas.py                    Pydantic request/response types
│   │   ├── models/db_models.py           ORM — Users, Requests, AIResults, AuditLogs
│   │   ├── routes/                       auth · analyze · design · techpack · admin
│   │   ├── services/
│   │   │   ├── llm_client.py             ★ Unified Anthropic/OpenAI/mock router
│   │   │   ├── orchestrator.py           Parallel fan-out + aggregation + fallback
│   │   │   ├── trend_service.py          F2 — trend prediction
│   │   │   ├── color_service.py          F4 — palette intelligence
│   │   │   ├── design_service.py         F5 — concept generation
│   │   │   └── nlp_service.py            F6 — tech pack generation
│   │   └── utils/
│   │       ├── prompts.py                ★ Versioned LLM prompts
│   │       └── logger.py                 Structured JSON-line logger
│   ├── .env.example                      ★ Copy → .env, paste your key
│   └── requirements.txt
├── frontend/                             React + Vite + React Router
│   ├── src/
│   │   ├── App.jsx                       ★ Login-first routing + <Protected>
│   │   ├── api.js                        Fetch client w/ bearer-token auth
│   │   ├── components/                   Nav, ConfidenceRing, Swatch, DesignCard
│   │   └── pages/
│   │       ├── Login.jsx                 ★ Landing-by-default, role picker on register
│   │       ├── Designer.jsx              Designer/admin workspace
│   │       ├── Browse.jsx                Shopper read-only view
│   │       ├── Results.jsx               Trends + colors + designs + tech pack
│   │       ├── History.jsx               Per-user request history
│   │       └── Admin.jsx                 Admin-only dashboard
│   └── package.json
├── preview.html                          Standalone UI preview (no backend needed)
├── start.sh                              One-shot dev runner
└── README.md                             You are here
```

Files marked ★ are the ones you'll likely touch when integrating.

---

## 🗺 How it maps to the SRS / FRS

| Spec                                        | Implementation                                                    |
| ------------------------------------------- | ----------------------------------------------------------------- |
| SRS §1.3 Components                         | `routes/`, `services/`, `models/`, `utils/`                       |
| SRS §2 AI Orchestrator (key differentiator) | `services/orchestrator.py` — parallel fan-out + aggregation       |
| SRS §3 PostgreSQL schema                    | `models/db_models.py` (works on SQLite too — default)             |
| SRS §4.1 `POST /auth/login`                 | `routes/auth.py`                                                  |
| SRS §4.2 `POST /analyze`                    | `routes/analyze.py`                                               |
| SRS §4.3 `GET /results/{id}`                | `routes/analyze.py`                                               |
| SRS §4.4 `POST /generate-design`            | `routes/design.py` (+ `/modify` for FRS F5 refinement)            |
| SRS §4.5 `POST /generate-techpack`          | `routes/techpack.py` + `/export` for JSON download                |
| SRS §4.6 `GET /admin/metrics`               | `routes/admin.py` (admin role required)                           |
| SRS §5.4 Orchestrator w/ fallback           | `services/orchestrator.py::process_request`                       |
| SRS §5.5 / FRS §8 Versioned prompts         | `utils/prompts.py`                                                |
| FRS F1 Guided UX, templates                 | `pages/Designer.jsx` — 6 prompt templates                         |
| FRS F2 Global Trend Intelligence            | `services/trend_service.py` — 5 region banks + LLM hook           |
| FRS F4 Color Intelligence                   | `services/color_service.py` — region-aware palettes               |
| FRS F5 AI Design Studio + "modify"          | `services/design_service.py`, `DesignCard.jsx`                    |
| FRS F6 Tech Pack generator + export         | `services/nlp_service.py`, `techpack/export` endpoint             |
| FRS F8 Confidence + explainability          | `ConfidenceRing.jsx`, `explanation` field on every result         |
| FRS F9 Admin Intelligence Dashboard         | `pages/Admin.jsx` — heatmap, distribution, top trends, CSV export |
| FRS F10 Audit, logging & compliance         | `AuditLog` model + versioned prompts + `/admin/audit-logs/export` |

---

## 🚀 Production checklist

- [ ] Set a strong `JWT_SECRET` in `.env`
- [ ] Switch `DATABASE_URL` to PostgreSQL (the SRS §3 schema already matches)
- [ ] Tighten CORS origins in `backend/app/main.py`
- [ ] Put the backend behind a reverse proxy (nginx/Caddy) with TLS
- [ ] Set real `ANTHROPIC_API_KEY` or `OPENAI_API_KEY`
- [ ] Consider rate-limiting `/analyze` per user
- [ ] Ship structured logs to your observability stack

## 📜 License

Generated for hackathon / demo use. Adapt freely.
