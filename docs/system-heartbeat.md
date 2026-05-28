# System Heartbeat — FakeStoreAPI Medallion Pipeline

**Last Updated:** 2026-05-27
**Status:** Silver/Gold ✅ complete; Vector text embeddings ✅ complete; Vector image embeddings ✅ fixed (local CLIP → BQ)

---

## Project Overview

This project implements a medallion architecture pipeline:
1. **Bronze:** Raw data extracted from FakeStoreAPI → stored in `data/` → uploaded to GCS
2. **Silver:** Data loaded into BigQuery with metadata columns
3. **Gold:** Transformed tables for analytics
4. **Vector:** Text embeddings ✅ complete (sentence-transformers); Image embeddings ✅ fixed (CLIP local); Vector search operativo

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
| **20 product images** | `gs://fakestore-raw/images/` | PNG files in GCS |
| **Vector SQL scaffolding** | `sql/vector/` | 01_create_dataset.sql done |
| **Notebook scaffolding** | `notebooks/vector_search_visualization.ipynb` | PCA + visualization structure created |
| **Kernel setup** | `scripts/setup_notebook_kernel.py` | Jupyter kernel registered for `.venv` |
| **ONNX model in GCS** | `gs://fakestore-raw/models/all-MiniLM-L6-v2.onnx` | Downloaded and uploaded (text embeddings) |
| **MobileNetV2 in GCS** | `gs://fakestore-raw/models/mobilenet_v2/mobilenet_v2_v2/` | SavedModel with serving signature uploaded |
| **Text embeddings pipeline** | `scripts/generate_embeddings.py` + `make vector` | 20 product embeddings (384-d) with sentence-transformers, in `fakestore_vector.vector_products` |
| **Image embeddings pipeline** | `scripts/generate_image_embeddings.py` + `make image-embeddings` | 20 product image embeddings (512-d) with CLIP, in `fakestore_vector.image_products` |
| **Vector index** | `sql/vector/04_create_vector_index.sql` | IVF index on `vector_products.embedding` for COSINE similarity |
| **Vector search queries** | `sql/vector/05_vector_search_examples.sql` | 4 example queries: product similarity, text-to-product, cross-category, avg distance |
| **End-to-end vector pipeline** | `Makefile` `vector` target | `make vector` runs: dataset → embeddings → index |

### ✅ COMPLETED: Vector Layer — Text Embeddings

**Logrado:** Se generaron 20 embeddings de producto (384 dimensiones) usando `sentence-transformers/all-MiniLM-L6-v2` localmente y se subieron a `fakestore_vector.vector_products`. El índice vectorial IVF y las queries de búsqueda están operativos.

**Pipeline ejecutado:**
```bash
make vector   # → vector-dataset → vector-embeddings → vector-index
```

**Archivos involucrados (text embeddings):**
- `scripts/generate_embeddings.py` — Lee `silver_products` de BQ, genera embeddings con sentence-transformers, sube a `vector_products`
- `sql/vector/02_import_onnx_model.sql` — Intento de importar ONNX en BQ (falló); se usa el fallback local
- `sql/vector/04_create_vector_index.sql` — IVF index creado ✅
- `sql/vector/05_vector_search_examples.sql` — 4 queries de ejemplo funcionales ✅

### ✅ FIXED: Vector Layer — Image Embeddings

**Solución:** Se implementó `scripts/generate_image_embeddings.py` que genera embeddings de imagen localmente usando CLIP (`clip-ViT-B-32`, 512 dimensiones) y los sube a `fakestore_vector.image_products` en BigQuery. Mismo patrón que las text embeddings: local Python → BQ, sin Vertex AI.

**Pipeline:**
```bash
make image-embeddings   # → descarga 20 imágenes → CLIP embed → upload a BQ
make image-index        # → crea índice vectorial (cuando exista el SQL)
```

**Archivos nuevos:**
- `scripts/generate_image_embeddings.py` — Lee `silver_products` de BQ, descarga imágenes desde URLs, genera embeddings con CLIP, sube a `image_products`

**Intentos fallidos previos (archivados):**

| # | Enfoque | Error |
|---|---------|-------|
| 1 | `ML.GENERATE_EMBEDDING` con ONNX en BQ | HuggingFace ONNX no cumple schema BQ |
| 2 | `ML.PREDICT` con MobileNetV2 TF Hub | TF Hub no expone serving signatures |
| 3 | MobileNetV2 classification wrapper | Produce 1001 clases, no feature vectors |

**Root cause de los intentos fallidos:** BigQuery no tiene modelos de embeddings built-in. La solución fue generar embeddings localmente (patrón ya validado con text embeddings) en vez de forzar la ejecución en BQ.

**Archivos heredados (no utilizados por la nueva solución):**
- `sql/vector/02_import_mobilenet_model.sql` — Obsoleto (intento BQ-nativo)
- `sql/vector/03_generate_image_embeddings.sql` — Obsoleto (intento BQ-nativo)
- `scripts/download_mobilenet_model.py` — Descarga classification model (no usado)

**Datos en GCS:**
- Imágenes: `gs://fakestore-raw/images/*.png` (20 archivos) ✅
- Modelo TF (clasificación): `gs://fakestore-raw/models/mobilenet_v2/mobilenet_v2_v2/` (no usado)

### 🔴 Pending (CI/CD Automation)

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
| BQ Datasets | `fakestore_raw`, `fakestore_silver`, `fakestore_gold`, `fakestore_vector` |
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

### Priority 1: Polish Image Embeddings

1. **Run the pipeline:** `make image-embeddings` para generar y subir los 20 embeddings de imagen
2. **Create image vector index SQL:** Crear `sql/vector/04_create_image_vector_index.sql` para el índice IVF en `image_products`
3. **Add cross-modal search:** Ampliar `sql/vector/05_vector_search_examples.sql` con queries que unan text + image embeddings
4. **Run notebook:** Abrir `notebooks/vector_search_visualization.ipynb` para visualizar ambos espacios de embeddings

### Priority 2: Unify Text + Image Embeddings

1. Opcional: fusionar `vector_products` (text) e `image_products` (image) en una sola tabla con dos columnas de embedding
2. Crear queries de búsqueda multimodal (texto → imagen, imagen → texto)

### Priority 3: Other tasks
1. **Add data quality checks:** Validate row counts, nulls, schema consistency in Silver/Gold tables
2. **Set up scheduling:** Use Cloud Scheduler or GitHub Actions to re-extract periodically
3. **Add Looker Studio dashboards:** Connect to Gold tables for visualization
4. **Implement incremental loads:** Add partitioning and clustering for cost optimization

---

## Troubleshooting

- **Auth errors:** Run `gcloud auth login` and verify project `gcloud config get-value project`
- **Bucket exists:** Use `-- overwrite` flag or check with `gcloud storage buckets describe gs://fakestore-raw`
- **BQ load failures:** Ensure NDJSON files are properly formatted (one JSON object per line)
- **ML.GENERATE_EMBEDDING with ONNX:** Model must have specific tensor names. HuggingFace models don't work directly.
- **TF SavedModel import:** Must have `serving_default` signature with proper input/output specs. TF Hub models often lack this.
- **Image embeddings blocked:** Solution was generating embeddings locally with `scripts/generate_image_embeddings.py` using CLIP, then uploading to BQ. Same proven pattern as text embeddings.
