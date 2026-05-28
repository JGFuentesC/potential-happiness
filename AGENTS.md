# FakeStoreAPI — Medallion Architecture Playbook

## Prerequisites

- **Python 3.12+** with `uv` (`curl -LsSf https://astral.sh/uv/install.sh | sh`)
- **gcloud CLI** autenticado (`gcloud auth login` && `gcloud config set project YOUR_PROJECT_ID`)
- **Billing** habilitado en el proyecto GCP

## Project Structure

```
.
├── data/                          # Raw data local (gitignored)
│   ├── products/{id}.json
│   ├── carts/{id}.json
│   ├── users/{id}.json
│   └── images/{filename}.png
├── scripts/
│   ├── .venv/                     # Virtual env (gitignored)
│   ├── extract_fakestore.py       # Async extraction script
│   └── download_images.py         # Async image downloader
├── AGENTS.md
└── .gitignore
```

## Step-by-step

### 1. Create virtual environment

```bash
uv venv scripts/.venv
uv pip install --python scripts/.venv/bin/python aiohttp aiofiles
```

### 2. Extract data from API

```bash
uv run --python scripts/.venv/bin/python scripts/extract_fakestore.py
```

Extracts **20 products**, **7 carts**, and **10 users** from `https://fakestoreapi.com`,
saving one JSON file per record under `data/{resource}/{id}.json`.

### 3. Download product images

```bash
uv run --python scripts/.venv/bin/python scripts/download_images.py
```

Downloads **20 PNG images** from product URLs to `data/images/`.

### 4. Create GCS bucket

```bash
gcloud storage buckets create gs://fakestore-raw \
  --location=us-east4 \
  --uniform-bucket-level-access
```

### 5. Upload data to GCS

```bash
gcloud storage cp data/products/*.json gs://fakestore-raw/products/
gcloud storage cp data/carts/*.json   gs://fakestore-raw/carts/
gcloud storage cp data/users/*.json   gs://fakestore-raw/users/
gcloud storage cp data/images/*.png   gs://fakestore-raw/images/
```

Build NDJSON consolidated files for BigQuery:

```bash
for resource in products carts users; do
  for f in data/$resource/*.json; do
    python3 -c "import json; print(json.dumps(json.load(open('$f')), separators=(',', ':')))"
  done > data/${resource}_all.json
done

gcloud storage cp data/products_all.json gs://fakestore-raw/products_all.ndjson
gcloud storage cp data/carts_all.json    gs://fakestore-raw/carts_all.ndjson
gcloud storage cp data/users_all.json    gs://fakestore-raw/users_all.ndjson
```

### 6. Create BigQuery dataset & tables

```bash
bq mk --dataset --location=us-east4 fakestore_raw

bq load --source_format=NEWLINE_DELIMITED_JSON --autodetect \
  fakestore_raw.raw_products \
  gs://fakestore-raw/products_all.ndjson

bq load --source_format=NEWLINE_DELIMITED_JSON --autodetect \
  fakestore_raw.raw_carts \
  gs://fakestore-raw/carts_all.ndjson

bq load --source_format=NEWLINE_DELIMITED_JSON --autodetect \
  fakestore_raw.raw_users \
  gs://fakestore-raw/users_all.ndjson
```

### 7. Add metadata columns

```bash
for tbl in raw_products raw_carts raw_users; do
  bq query --nouse_legacy_sql \
    "ALTER TABLE fakestore_raw.$tbl
       ADD COLUMN IF NOT EXISTS _ingested_at TIMESTAMP,
       ADD COLUMN IF NOT EXISTS _source STRING,
       ADD COLUMN IF NOT EXISTS _gcs_uri STRING,
       ADD COLUMN IF NOT EXISTS _source_file STRING;"
done
```

### 8. Populate metadata

```bash
bq query --nouse_legacy_sql "
  UPDATE fakestore_raw.raw_products
     SET _ingested_at = CURRENT_TIMESTAMP(),
         _source = '/products',
         _gcs_uri = 'gs://fakestore-raw/products_all.ndjson',
         _source_file = CONCAT('gs://fakestore-raw/products/', CAST(id AS STRING), '.json')
   WHERE TRUE;

  UPDATE fakestore_raw.raw_carts
     SET _ingested_at = CURRENT_TIMESTAMP(),
         _source = '/carts',
         _gcs_uri = 'gs://fakestore-raw/carts_all.ndjson',
         _source_file = CONCAT('gs://fakestore-raw/carts/', CAST(id AS STRING), '.json')
   WHERE TRUE;

  UPDATE fakestore_raw.raw_users
     SET _ingested_at = CURRENT_TIMESTAMP(),
         _source = '/users',
         _gcs_uri = 'gs://fakestore-raw/users_all.ndjson',
         _source_file = CONCAT('gs://fakestore-raw/users/', CAST(id AS STRING), '.json')
   WHERE TRUE;
"
```

## Tables: schema & row counts

| Table | Rows | Notes |
|-------|------|-------|
| `raw_products` | 20 | Includes nested `rating { rate, count }` |
| `raw_carts` | 7 | Includes `date`, `__v`, and repeated `products { productId, quantity }` |
| `raw_users` | 10 | Includes nested `name { firstname, lastname }`, `address { street, city, zipcode, number, geolocation { lat, long } }`, `phone`, `__v` |

## GCS Bucket layout

```
gs://fakestore-raw/
├── products/{id}.json        # 20 files
├── carts/{id}.json           # 7 files
├── users/{id}.json           # 10 files
├── images/{filename}.png     # 20 files
├── products_all.ndjson       # consolidated for BQ
├── carts_all.ndjson
└── users_all.ndjson
```

## Configuration parameters

| Parameter | Value |
|-----------|-------|
| API Base URL | `https://fakestoreapi.com` |
| GCS Bucket | `gs://fakestore-raw` |
| BQ Dataset | `fakestore_raw` |
| GCP Region | `us-east4` |

> **Note:** All GCP commands assume your active `gcloud` project is correctly set.
> No secrets, API keys, or project IDs are hardcoded — configure via `gcloud config`.
