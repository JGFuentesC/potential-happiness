# System Heartbeat — FakeStoreAPI Medallion Pipeline

**Last Updated:** 2026-05-27
**Status:** Initial scaffolding complete; data extraction ready

---

## Project Overview

This project implements a medallion architecture pipeline:
1. **Bronze:** Raw data extracted from FakeStoreAPI → stored in `data/` → uploaded to GCS
2. **Silver:** Data loaded into BigQuery with metadata columns
3. **Gold:** (Planned) Transformed tables for analytics

---

## Current State

### ✅ Completed

| Component | Path | Notes |
|-----------|------|-------|
| Playbook | `AGENTS.md` | Step-by-step workflow for extraction → GCS → BigQuery |
| Extract script | `scripts/extract_fakestore.py` | Async extraction of 20 products, 7 carts, 10 users |
| Image downloader | `scripts/download_images.py` | Async download of 20 product images |
| Documentation | `docs/medallion-architecture.md` | Architecture diagrams and design |
| Sample data | `docs/docs-data.json` | JSON reference data |

### 🔴 Pending (Manual Execution Required)

All steps below require manual execution or CI/CD automation:

1. **Local extraction:**
   ```bash
   uv venv scripts/.venv
   uv pip install --python scripts/.venv/bin/python aiohttp aiofiles
   uv run --python scripts/.venv/bin/python scripts/extract_fakestore.py
   ```

2. **Download images:**
   ```bash
   uv run --python scripts/.venv/bin/python scripts/download_images.py
   ```

3. **GCS bucket creation:** (Check if `gs://fakestore-raw` exists)
   ```bash
   gcloud storage buckets create gs://fakestore-raw \
     --location=us-east4 \
     --uniform-bucket-level-access
   ```

4. **Upload to GCS:** (Requires gcloud auth)
   ```bash
   gcloud storage cp data/products/*.json gs://fakestore-raw/products/
   # ... same for carts, users, images
   ```

5. **Create NDJSON files:**
   ```bash
   # Scripts produce individual JSON files; consolidate per AGENTS.md step 5
   ```

6. **BigQuery setup:**
   ```bash
   bq mk --dataset --location=us-east4 fakestore_raw
   bq load --source_format=NEWLINE_DELIMITED_JSON --autodetect \
     fakestore_raw.raw_products gs://fakestore-raw/products_all.ndjson
   # ... same for carts, users
   ```

---

## Configuration

| Parameter | Value |
|-----------|-------|
| API Base URL | `https://fakestoreapi.com` |
| GCS Bucket | `gs://fakestore-raw` |
| BQ Dataset | `fakestore_raw` |
| GCP Region | `us-east4` |

**Credentials:** Uses `gcloud auth` (no hardcoded secrets). Ensure `gcloud config set project YOUR_PROJECT_ID` is configured.

---

## Data Schema Summary

### `raw_products` (20 rows)
```json
{ "id", "title", "price", "description", "category", "image", "rating": { "rate", "count" } }
```

### `raw_carts` (7 rows)
```json
{ "id", "userId", "date", "products": [{ "productId", "quantity" }], "__v" }
```

### `raw_users` (10 rows)
```json
{ "id", "email", "username", "password", "name": { "firstname", "lastname" },
  "address": { "street", "city", "zipcode", "number", "geolocation": { "lat", "long" } },
  "phone", "__v" }
```

> ⚠️ **Note:** Raw user data contains plaintext passwords from FakeStoreAPI. Do not expose in downstream Gold tables.

---

## Next Agent Tasks

1. **Automate extraction:** Convert manual `uv run` commands into a `Makefile` or `justfile`
2. **Implement Silver layer:** Create BQ views/scripts that transform Bronze → Silver
3. **Add data quality checks:** Validate row counts, nulls, schema consistency
4. **Set up scheduling:** Use Cloud Scheduler or GitHub Actions to re-extract periodically
5. **Implement Gold layer:** Create aggregation tables for analytics/reporting

---

## Troubleshooting

- **Auth errors:** Run `gcloud auth login` and verify project `gcloud config get-value project`
- **Bucket exists:** Use `-- overwrite` flag or check with `gcloud storage buckets describe gs://fakestore-raw`
- **BQ load failures:** Ensure NDJSON files are properly formatted (one JSON object per line)
