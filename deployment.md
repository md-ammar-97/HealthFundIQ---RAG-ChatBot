# HealthFundIQ — Deployment Guide

**Stack:** Qdrant Cloud · GitHub · Railway (backend) · Vercel (frontend)

---

## 0. Production Architecture

```
┌──────────────────────────────────────────────────────────────┐
│  GitHub Actions                                               │
│  deploy.yml  ── on push to main ──► Railway + Vercel         │
│  daily-ingestion.yml  ── cron 10:00 AM IST ──► Qdrant Cloud  │
└─────────────────────────────────────────────────────────────-┘

Browser / User
        │
        ▼
┌──────────────────────────────────────────┐
│  Vercel (frontend)                        │
│  Next.js 14 · Port 443 (HTTPS)           │
│  Repo: frontend/ directory               │
└──────────────┬───────────────────────────┘
               │  HTTPS REST  (NEXT_PUBLIC_API_URL)
               ▼
┌──────────────────────────────────────────┐
│  Railway (backend)                        │
│  FastAPI — pure web server               │
│  No in-process scheduler                 │
└──────┬────────────┬───────────────────────┘
       │            │
       ▼            ▼
 Groq API     Qdrant Cloud
 (LLM +       (vector store —
  classifier)   ~400 chunks)
```

---

## 1. Prerequisites

| Tool | Version | Purpose |
|---|---|---|
| Python | 3.11+ | Backend runtime |
| Node.js | 18+ | Frontend build |
| Git | any | Version control |
| Railway CLI | latest | Backend deploy |
| Vercel CLI | latest | Frontend deploy |
| Playwright | via pip | Dynamic scraping |

```bash
# Install Railway CLI
npm install -g @railway/cli

# Install Vercel CLI
npm install -g vercel

# Install Playwright browsers (backend only)
playwright install chromium
```

---

## 2. Repository Setup (GitHub)

### 2.1 Initialize and Push

```bash
cd C:\Users\PF56J\ClaudeProjects\FinanceBot

git init
git add .
git commit -m "Initial commit — HealthFundIQ RAG Bot"
git branch -M main
git remote add origin https://github.com/<your-username>/healthfundiq.git
git push -u origin main
```

### 2.2 `.gitignore`

Create or verify `.gitignore` contains:

```gitignore
# Secrets
.env
*.env.local

# Python
__pycache__/
*.py[cod]
.pytest_cache/
*.egg-info/
dist/
build/

# Data (large files — do not commit raw HTML/PDF)
data/raw/
vectorstore/

# Models (downloaded at runtime)
.cache/
models/

# Node
frontend/node_modules/
frontend/.next/
frontend/.vercel/

# Logs
logs/*.log
```

### 2.3 Repository Structure

```
healthfundiq/
├── api/                    # FastAPI backend
├── config/                 # sources.yaml, settings.py, normalization.yaml
├── embeddings/             # Qdrant store + BGE embedder
├── frontend/               # Next.js 14 app (deployed separately to Vercel)
├── guardrails/
├── ingestion/              # Crawler, parser, normalizer, chunker
├── llm/
├── retrieval/
├── scheduler/
├── data/parsed/            # Committed: clean JSON fund profiles
├── requirements.txt
├── Procfile                # Railway start command
├── railway.json            # Railway config
└── .env.example
```

**Commit `data/parsed/`** — these are small JSON files (~50KB total) that the structured lookup reads at runtime. Do NOT commit `data/raw/` (HTML/PDF files, ~tens of MB).

---

## 3. Qdrant Cloud Setup

### 3.1 Create a Cluster

1. Go to [cloud.qdrant.io](https://cloud.qdrant.io)
2. Create a free-tier cluster (1 GB RAM, sufficient for ~400 chunks × 768-dim)
3. Note your **cluster URL**: `https://<cluster-id>.<region>.gcp.cloud.qdrant.io`
4. Create an **API key** in the cluster settings

### 3.2 Collection Setup

The collection is created automatically on first `ingestion run` or `upsert_chunks` call. The `_ensure_collection()` function in `embeddings/store.py` handles:

- Creates collection `healthcare_funds` with cosine distance and 768-dim vectors
- Creates payload indices for `fund_id`, `country`, `section`, `ticker`, `isin`, `source_type`, `domain_subcategory`

You can also create it manually via Qdrant Cloud dashboard or the CLI:

```python
# Manual collection creation (run once)
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams

client = QdrantClient(
    url="https://<cluster-id>.gcp.cloud.qdrant.io",
    api_key="your_api_key",
)
client.create_collection(
    collection_name="healthcare_funds",
    vectors_config=VectorParams(size=768, distance=Distance.COSINE),
)
```

### 3.3 Initial Ingestion (Populate Qdrant)

After deploying the backend (or locally with cloud credentials), run ingestion:

```bash
# Set cloud credentials in .env first, then:
python -m ingestion.run_ingestion
```

This fetches all 34 active funds, processes them, and populates Qdrant Cloud. Expected time: 30–60 minutes (rate-limited fetches + Playwright for India funds).

### 3.4 Migration from ChromaDB (if applicable)

If you have an existing ChromaDB collection and want to migrate data without re-fetching:

```bash
# Re-run from existing parsed JSON (no network calls)
python -m ingestion.backfill_parsed
```

This reads `data/parsed/**/*.json`, chunks them, embeds them, and upserts into Qdrant. The `data/parsed/` directory should be committed to the repo.

---

## 4. Backend Deployment (Railway)

### 4.1 Add Deployment Files

**`Procfile`** (root of repo):

```
web: uvicorn api.main:app --host 0.0.0.0 --port $PORT
```

**`railway.json`** (root of repo):

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "uvicorn api.main:app --host 0.0.0.0 --port $PORT",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 3
  }
}
```

**`runtime.txt`** (root of repo, for Python version):

```
python-3.11.9
```

### 4.2 Deploy to Railway

```bash
# Log in
railway login

# Create project (first time)
railway init

# Link existing project (subsequent times)
railway link

# Deploy
railway up
```

Or connect GitHub for automatic deploys: Railway Dashboard → New Project → Deploy from GitHub → select `healthfundiq` → set branch to `main`.

### 4.3 Environment Variables on Railway

Set these in Railway Dashboard → Variables:

```
GROQ_API_KEY=<your_groq_api_key>
GROQ_MODEL=llama-3.3-70b-versatile
GROQ_CLASSIFIER_MODEL=llama-3.1-8b-instant
EMBEDDING_MODEL=intfloat/multilingual-e5-base
QDRANT_URL=https://<cluster-id>.gcp.cloud.qdrant.io
QDRANT_API_KEY=<your_qdrant_api_key>
QDRANT_COLLECTION=healthcare_funds
TOP_K_RETRIEVAL=6
SCHEDULER_HOUR_IST=10
FASTAPI_HOST=0.0.0.0
LOG_LEVEL=INFO
```

**Do not set `PORT`** — Railway injects it automatically.

### 4.4 Playwright on Railway

Playwright requires Chromium. Add a build command in `railway.json` or use a Nixpacks `nixpacks.toml`:

**`nixpacks.toml`** (root of repo):

```toml
[phases.setup]
nixPkgs = ["chromium", "nss", "nspr", "atk", "cups", "libdrm", "dbus", "expat", "libxkbcommon"]

[phases.build]
cmds = ["pip install -r requirements.txt", "playwright install chromium"]
```

Alternatively, set this Railway environment variable to skip Playwright and fall back to static fetching:
```
PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1
```
(Only do this if you can confirm all fund sources are parseable without JS rendering.)

### 4.5 Embedding Model

The default model is `intfloat/multilingual-e5-base` (~278 MB, 768-dim). It supports 100 languages including English and downloads in ~15 seconds on Railway's builders. No special handling needed — startup time is under 30 seconds.

**If you ever need to swap models**, update two places and re-run ingestion:

| Setting | File | Value |
|---|---|---|
| `embedding_model` default | `config/settings.py` | model HF ID |
| `_VECTOR_DIM` | `embeddings/store.py` | model output dimension |
| `EMBEDDING_MODEL` | `.github/workflows/daily-ingestion.yml` | same HF ID |

You must also **delete and recreate the Qdrant collection** when the dimension changes (Qdrant collections are fixed-dimension).

### 4.6 Verify Backend

```bash
# Health check
curl https://<your-railway-app>.up.railway.app/health

# Expected:
# {"status":"ok","timestamp":"2026-06-04T...","corpus_chunks":400}
```

---

## 5. Frontend Deployment (Vercel)

### 5.1 Configure Next.js for Vercel

**`frontend/vercel.json`**:

```json
{
  "framework": "nextjs",
  "outputDirectory": ".next",
  "installCommand": "npm install",
  "buildCommand": "npm run build",
  "devCommand": "npm run dev"
}
```

**`frontend/next.config.js`** — add backend URL to allowed origins:

```js
/** @type {import('next').NextConfig} */
const nextConfig = {
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: `${process.env.NEXT_PUBLIC_API_URL}/:path*`,
      },
    ];
  },
};
module.exports = nextConfig;
```

### 5.2 Deploy to Vercel

```bash
cd frontend
vercel login
vercel
# Follow prompts: link to existing project or create new
# Set root directory: frontend
# Framework: Next.js
```

Or connect GitHub: Vercel Dashboard → Add New Project → Import from GitHub → select `healthfundiq` → set **Root Directory** to `frontend`.

### 5.3 Environment Variables on Vercel

Set in Vercel Dashboard → Project → Settings → Environment Variables:

```
NEXT_PUBLIC_API_URL=https://<your-railway-app>.up.railway.app
```

This variable is read by the Next.js frontend to call the Railway backend. It must be prefixed with `NEXT_PUBLIC_` to be available in the browser.

### 5.4 Verify Frontend

```bash
# Health check via the frontend's rewrite proxy
curl https://<your-vercel-app>.vercel.app/api/health
```

---

## 6. CORS Configuration

The Railway backend must allow requests from the Vercel frontend origin. Update `api/main.py`:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://<your-vercel-app>.vercel.app",
        "https://healthfundiq.vercel.app",  # custom domain if set
        "http://localhost:3000",             # local dev
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)
```

---

## 7. Environment Summary

| Variable | Local (`.env`) | Railway | Vercel |
|---|---|---|---|
| `GROQ_API_KEY` | ✓ | ✓ | — |
| `GROQ_MODEL` | optional | ✓ | — |
| `GROQ_CLASSIFIER_MODEL` | optional | ✓ | — |
| `EMBEDDING_MODEL` | optional | ✓ | — |
| `QDRANT_URL` | ✓ (cloud) or empty (local) | ✓ | — |
| `QDRANT_API_KEY` | ✓ (cloud) or empty (local) | ✓ | — |
| `QDRANT_COLLECTION` | optional | optional | — |
| `QDRANT_LOCAL_PATH` | ✓ (dev only) | — | — |
| `TOP_K_RETRIEVAL` | optional | optional | — |
| `SCHEDULER_HOUR_IST` | optional | optional | — |
| `LOG_LEVEL` | optional | optional | — |
| `NEXT_PUBLIC_API_URL` | set in `frontend/.env.local` | — | ✓ |

---

## 8. CI/CD Pipeline (GitHub Actions)

Two workflow files live in `.github/workflows/`.

### 8.1 `deploy.yml` — Deploy on Push to Main

Triggered on every push to `main`, but **skips** when only `data/parsed/` or `.md` files changed (so ingestion commits don't trigger unnecessary redeploys).

File already created at `.github/workflows/deploy.yml`. Add these secrets in GitHub → Settings → Secrets and variables → Actions:

| Secret | Where to get it |
|---|---|
| `RAILWAY_TOKEN` | Railway Dashboard → Account → Tokens |
| `VERCEL_TOKEN` | Vercel Dashboard → Account → Tokens |
| `VERCEL_ORG_ID` | Vercel project settings |
| `VERCEL_PROJECT_ID` | Vercel project settings |

### 8.2 `daily-ingestion.yml` — Daily Corpus Refresh

Triggered by cron at **4:30 AM UTC (= 10:00 AM IST)** and manually via `workflow_dispatch`.

File already created at `.github/workflows/daily-ingestion.yml`. This workflow:
1. Checks out the repo
2. Installs Python 3.11 + all dependencies + Playwright Chromium
3. Runs `python -m ingestion.run_ingestion` (fetches all 34 active funds, updates Qdrant Cloud)
4. Commits updated `data/parsed/**/*.json` back with `[skip ci]` tag (prevents deploy re-trigger)
5. Pushes to `main`

Add these secrets (in addition to the deploy secrets above):

| Secret | Where to get it |
|---|---|
| `GROQ_API_KEY` | [console.groq.com](https://console.groq.com) |
| `QDRANT_URL` | Qdrant Cloud Dashboard → Cluster → URL |
| `QDRANT_API_KEY` | Qdrant Cloud Dashboard → Cluster → API Keys |

**Manual trigger:** GitHub → Actions tab → Daily Corpus Ingestion → Run workflow. You can optionally pass a `fund_id` to re-ingest only one fund.

---

## 9. Scheduled Ingestion

Ingestion is handled entirely by **GitHub Actions** — `apscheduler` and `pytz` are not in `requirements.txt` and the Railway backend runs as a pure web server with no in-process cron.

### How it works

```
GitHub cron (4:30 AM UTC = 10:00 AM IST)
    → ubuntu-latest runner
    → pip install + playwright install chromium
    → python -m ingestion.run_ingestion
        → fetches 34 funds (Groww/ETF.com/TMX/Yahoo/JustETF/…)
        → tries backup_platform_urls when primary parse misses fields
        → updates Qdrant Cloud (upsert ~400 chunks)
        → writes data/parsed/**/*.json
    → git commit data/parsed/ "[skip ci]"
    → git push → main branch updated
```

### Verify ingestion ran

GitHub → Actions tab → Daily Corpus Ingestion → latest run. Each run logs per-fund results: `upserted=N`, `fields_missing=[…]`.

### Manual trigger options

**Option A — GitHub UI (recommended):**
GitHub → Actions → Daily Corpus Ingestion → Run workflow

**Option B — GitHub CLI:**
```bash
gh workflow run daily-ingestion.yml
```

**Option C — Admin HTTP endpoint (Railway shell, emergency only):**
```bash
# Railway Dashboard → Service → Shell
python -m ingestion.run_ingestion
```

### Ingestion run time

| Stage | Time |
|---|---|
| Static fetches (34 × 2 URLs) | ~5 min |
| Playwright fetches (India × 5 funds) | ~10 min |
| Backup URL fetches (when needed) | ~5 min |
| Embed + Qdrant upsert | ~2 min |
| **Total** | **~20–30 min** |

GitHub Actions free tier allows 2,000 minutes/month — a 30-min daily run uses ~900 min/month, well within the free limit.

---

## 10. Post-Deployment Verification Checklist

```
[ ] GET /health returns {"status":"ok","corpus_chunks":N} where N > 300
[ ] POST /chat with {"query":"What is the expense ratio of XLV?"} returns an answer
[ ] POST /chat with {"query":"Should I buy XLV?"} returns a refusal
[ ] Frontend loads at Vercel URL without console errors
[ ] Follow-up chips append fund name (e.g. "Show AUM for Health Care Select Sector SPDR ETF")
[ ] Fund Explorer shows funds with populated fields (not all "Not found in corpus")
[ ] Sources panel shows correct official/platform URLs
[ ] Qdrant Cloud dashboard shows ~400 points in healthcare_funds collection
[ ] Railway logs show no critical errors
[ ] CORS: frontend can call backend without 403/blocked headers
```

---

## 11. Monitoring and Maintenance

### 11.1 Logs

| Log | Location |
|---|---|
| Backend stdout | Railway Dashboard → Logs |
| Ingestion details | `logs/ingestion.log` (persisted in Railway volume) |
| Frontend errors | Vercel Dashboard → Functions |

### 11.2 Key Metrics to Watch

- **Qdrant collection count** — should be ~400; drop means ingestion failed
- **Groq API latency** — `/health` fetch_timestamp freshness
- **Ingestion success rate** — check `logs/ingestion.log` for `chunks_upserted=0` entries

### 11.3 Qdrant Cloud Limits (Free Tier)

| Limit | Value |
|---|---|
| RAM | 1 GB |
| Storage | 1 GB |
| Collections | 1 |
| API requests | Unlimited |

~400 chunks × 768-dim × 4 bytes ≈ 1.2 MB. Well within free tier.

### 11.4 Railway Limits (Hobby Plan)

| Limit | Value |
|---|---|
| RAM | 512 MB |
| CPU | 0.5 vCPU |
| Egress | 100 GB/mo |

`intfloat/multilingual-e5-base` uses ~400 MB RAM — fits comfortably within the Hobby plan's allocation.

---

## 12. Local Development Workflow

```bash
# 1. Clone repo
git clone https://github.com/<username>/healthfundiq.git
cd healthfundiq

# 2. Backend
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt
playwright install chromium
cp .env.example .env
# Edit .env: add GROQ_API_KEY; leave QDRANT_URL empty for local Qdrant

# 3. Run initial ingestion (populates local Qdrant)
python -m ingestion.run_ingestion

# 4. Start backend
uvicorn api.main:app --reload --port 8002

# 5. Frontend (separate terminal)
cd frontend
npm install
# Create frontend/.env.local:
# NEXT_PUBLIC_API_URL=http://localhost:8002
npm run dev
# → http://localhost:3000
```

---

## 13. Updating Sources After Deployment

When adding new funds to `config/sources.yaml`:

1. Add the new fund entry with `backup_platform_urls`
2. Commit and push to GitHub (triggers Railway deploy for the backend change)
3. Trigger ingestion manually: GitHub → Actions → Daily Corpus Ingestion → Run workflow
4. `data/parsed/` JSONs are committed automatically by the workflow

When changing backup source URLs:
- Edit `config/sources.yaml`
- Push to GitHub
- Re-run ingestion for affected funds only (manual shell command on Railway)

---

## 14. Rollback

**Backend** (Railway): Railway Dashboard → Service → Deployments → select previous → Redeploy

**Frontend** (Vercel): Vercel Dashboard → Project → Deployments → select previous → Promote to Production

**Qdrant data**: Qdrant does not auto-backup on free tier. The `data/parsed/` JSON files in the repo are the source of truth. To restore: run `python -m ingestion.backfill_parsed` after connecting to Qdrant.

---

## 15. Domain Configuration (Optional)

### Custom Domain on Vercel

Vercel Dashboard → Project → Settings → Domains → Add Domain → `healthfundiq.com`

Update CORS in `api/main.py`:
```python
allow_origins=["https://healthfundiq.com", "https://www.healthfundiq.com", ...]
```

### Custom Domain on Railway

Railway Dashboard → Service → Settings → Networking → Custom Domain → `api.healthfundiq.com`

Update `NEXT_PUBLIC_API_URL` in Vercel:
```
NEXT_PUBLIC_API_URL=https://api.healthfundiq.com
```
