# System Heartbeat — FakeStoreAPI Medallion Pipeline

**Last Updated:** 2026-05-27
**Status:** Silver and Gold layers complete; full pipeline operational

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
| **Bronze layer** | `fakestore_raw` dataset | 20 products, 7 carts, 10 users in BigQuery |
| **Silver layer** | `fakestore_silver` dataset | 4 tables: products, users, carts, cart_summary |
| **Gold layer** | `fakestore_gold` dataset | 3 tables: product_performance, user_behavior, category_insights |
| **SQL scripts** | `sql/silver/`, `sql/gold/` | 7 SQL files for transformations |
| **Makefile** | `Makefile` | `make silver`, `make gold`, `make verify`, `make clean` |

### 🔴 Pending (CI/CD Automation)

All core transformations are implemented and tested. Remaining work focuses on automation:

1. **Automate extraction:** Convert manual `uv run` commands into a `Makefile` target (already partially done)
2. **Add data quality checks:** Validate row counts, nulls, schema consistency
3. **Set up scheduling:** Use Cloud Scheduler or GitHub Actions to re-extract periodically
4. **Add Looker Studio dashboards:** Connect to Gold tables for visualization

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

1. **Add data quality checks:** Validate row counts, nulls, schema consistency in Silver/Gold tables
2. **Set up scheduling:** Use Cloud Scheduler or GitHub Actions to re-extract periodically
3. **Add Looker Studio dashboards:** Connect to Gold tables for visualization
4. **Implement incremental loads:** Add partitioning and clustering for cost optimization

---

## Troubleshooting

- **Auth errors:** Run `gcloud auth login` and verify project `gcloud config get-value project`
- **Bucket exists:** Use `-- overwrite` flag or check with `gcloud storage buckets describe gs://fakestore-raw`
- **BQ load failures:** Ensure NDJSON files are properly formatted (one JSON object per line)
