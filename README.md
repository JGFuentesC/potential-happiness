# FakeStoreAPI — Medallion Data Pipeline

A medallion architecture data pipeline that extracts e-commerce data from [FakeStoreAPI](https://fakestoreapi.com), ingests it into Google Cloud Storage and BigQuery, and transforms it through Bronze → Silver → Gold layers for analytics.

## Architecture

```
FakeStoreAPI ──> GCS (Bronze) ──> BigQuery (Silver) ──> BigQuery (Gold)
```

| Layer | Dataset | Description |
|-------|---------|-------------|
| Bronze | `fakestore_raw` | Raw JSON from API, as-is |
| Silver | `fakestore_silver` | Cleaned, typed, unnested, PII-redacted |
| Gold | `fakestore_gold` | Business aggregates for dashboards |

## Quick Start

### Prerequisites

- **Python 3.12+** with [uv](https://docs.astral.sh/uv/)
- **gcloud CLI** authenticated (`gcloud auth login`)
- **BigQuery API** enabled in your GCP project

### Setup

```bash
# 1. Configure your project
cp .env.example .env
# Edit .env with your GCP project ID

# 2. Install dependencies
uv venv scripts/.venv
uv pip install --python scripts/.venv/bin/python aiohttp aiofiles

# 3. Extract data from API
uv run --python scripts/.venv/bin/python scripts/extract_fakestore.py
uv run --python scripts/.venv/bin/python scripts/download_images.py

# 4. Upload to GCS and load into BigQuery (see AGENTS.md for full steps)

# 5. Run transformations
make silver   # Bronze → Silver
make gold     # Silver → Gold
make verify   # Check row counts
```

## Project Structure

```
.
├── data/                          # Raw data (gitignored)
├── scripts/
│   ├── extract_fakestore.py       # Async API extraction
│   └── download_images.py         # Async image downloader
├── sql/
│   ├── silver/                    # Bronze → Silver SQL
│   └── gold/                      # Silver → Gold SQL
├── docs/
│   ├── medallion-architecture.md  # Architecture design
│   └── system-heartbeat.md        # Project status
├── .env.example                   # BQ config template
├── Makefile                       # Pipeline automation
└── AGENTS.md                      # Step-by-step playbook
```

## Makefile Commands

| Command | Description |
|---------|-------------|
| `make datasets` | Create Silver and Gold BQ datasets |
| `make silver` | Run all Silver transformations |
| `make gold` | Run Silver + Gold transformations |
| `make all` | Full pipeline + verify |
| `make verify` | Show row counts across all layers |
| `make clean` | Drop Silver and Gold tables |

## Tables

| Table | Rows | Description |
|-------|------|-------------|
| `raw_products` | 20 | Raw products with nested rating |
| `raw_carts` | 7 | Raw carts with product arrays |
| `raw_users` | 10 | Raw users with nested address/name |
| `silver_products` | 20 | Cleaned products, extracted ratings |
| `silver_users` | 10 | Users with redacted passwords |
| `silver_carts` | 14 | Unnested cart items |
| `silver_cart_summary` | 7 | Denormalized cart view |
| `gold_product_performance` | 20 | Product ranking by revenue |
| `gold_user_behavior` | 10 | User segmentation |
| `gold_category_insights` | 4 | Category-level analytics |

## Security

- No secrets, API keys, or project IDs are hardcoded
- Credentials managed via `gcloud auth`
- User passwords are redacted in Silver layer
- Sensitive files (`.env`, `.gcloud_config/`, `data/`) are gitignored

## Documentation

- [AGENTS.md](AGENTS.md) — Full step-by-step playbook
- [docs/medallion-architecture.md](docs/medallion-architecture.md) — Architecture design
- [docs/system-heartbeat.md](docs/system-heartbeat.md) — Current project status
