# FakeStoreAPI — Arquitectura Medallón en GCP

## Fuente

| Propiedad | Valor |
|-----------|-------|
| API Base URL | `https://fakestoreapi.com` |
| API Name | FakeStoreAPI v2.1.11 |
| Tipo | REST (fake e-commerce) |
| Formato | JSON |

---

## Endpoints

| Método | Path | Descripción | Response Schema |
|--------|------|-------------|----------------|
| GET | `/products` | Listar todos los productos | `Product[]` |
| POST | `/products` | Crear producto | `Product` |
| GET | `/products/{id}` | Obtener producto por ID | `Product` |
| PUT | `/products/{id}` | Actualizar producto | `Product` |
| DELETE | `/products/{id}` | Eliminar producto | — |
| GET | `/carts` | Listar todos los carritos | `Cart[]` |
| POST | `/carts` | Crear carrito | `Cart` |
| GET | `/carts/{id}` | Obtener carrito por ID | `Cart` |
| PUT | `/carts/{id}` | Actualizar carrito | `Cart` |
| DELETE | `/carts/{id}` | Eliminar carrito | — |
| GET | `/users` | Listar todos los usuarios | `User[]` |
| POST | `/users` | Crear usuario | `User` |
| GET | `/users/{id}` | Obtener usuario por ID | `User` |
| PUT | `/users/{id}` | Actualizar usuario | `User` |
| DELETE | `/users/{id}` | Eliminar usuario | — |
| POST | `/auth/login` | Autenticar usuario | `LoginResponse` |

---

## Schemas (raw de la API)

### Product
| Campo | Tipo | Formato |
|-------|------|---------|
| id | integer | |
| title | string | |
| price | number | float |
| description | string | |
| category | string | |
| image | string | uri |

### Cart
| Campo | Tipo | Items |
|-------|------|-------|
| id | integer | |
| userId | integer | |
| products | array | `Product` (ver nota) |

> **Nota:** El spec referencias `Product` completo dentro de `Cart.products`, pero la API real retorna objetos con `{ productId, quantity }`. Habrá que mapear.

### User
| Campo | Tipo |
|-------|------|
| id | integer |
| username | string |
| email | string |
| password | string |

### Login (request body)
| Campo | Tipo |
|-------|------|
| username | string |
| password | string |

### LoginResponse
| Campo | Tipo |
|-------|------|
| token | string |

---

## Arquitectura Medallón

### Capa Bronze (raw ingestion)

Datos tal cual llegan de la API, persistidos en **Cloud Storage (Parquet/JSON)** y opcionalmente tabla externa en **BigQuery**.

| Tabla | Endpoint(s) | Estrategia |
|-------|-------------|------------|
| `bronze_products` | `GET /products` + `GET /products/{id}` | Full load diario / On-demand |
| `bronze_carts` | `GET /carts` + `GET /carts/{id}` | Full load diario |
| `bronze_users` | `GET /users` + `GET /users/{id}` | Full load diario |
| `bronze_logins` | `POST /auth/login` (log-only) | Solo si se capturan logs de auth |

**Herramientas sugeridas:**
- **Cloud Composer / Cloud Functions** con Python/`requests` para extracción
- **Cloud Storage** (`gs://raw-fakestore/bronze/{entity}/`)
- **BigQuery tablas externas** o carga con `bq load` / Dataflow

### Capa Silver (cleansed & structured)

Datos limpiados, tipados correctamente, deduplicados y con joins básicos. Modelo relacional (star schema).

#### `silver_products`
```sql
CREATE OR REPLACE TABLE silver_products AS
SELECT
  id AS product_id,
  title,
  CAST(price AS FLOAT64) AS price,
  description,
  LOWER(TRIM(category)) AS category,
  image AS image_url,
  PARSE_TIMESTAMP('%Y-%m-%dT%H:%M:%S', _ingested_at) AS ingested_at
FROM bronze_products;
```

#### `silver_users`
```sql
CREATE OR REPLACE TABLE silver_users AS
SELECT
  id AS user_id,
  username,
  LOWER(TRIM(email)) AS email,
  '(redacted)' AS password_hash,  -- nunca exponer password real
  ingested_at
FROM bronze_users;
```

#### `silver_carts`
```sql
CREATE OR REPLACE TABLE silver_carts AS
SELECT
  c.id AS cart_id,
  c.userId AS user_id,
  p.product_id,
  p.quantity,
  c.ingested_at
FROM bronze_carts c,
UNNEST(c.products) AS p;   -- asumiendo array de { productId, quantity }
```

#### `silver_cart_summary` (carts denormalized)
```sql
CREATE OR REPLACE TABLE silver_cart_summary AS
SELECT
  c.cart_id,
  c.user_id,
  u.username,
  ARRAY_AGG(STRUCT(p.product_id, p.title, p.price, sc.quantity)) AS items,
  SUM(p.price * sc.quantity) AS total_amount,
  COUNT(sc.product_id) AS item_count,
  c.ingested_at
FROM silver_carts c
JOIN silver_users u ON c.user_id = u.user_id
JOIN silver_products p ON c.product_id = p.product_id
GROUP BY c.cart_id, c.user_id, u.username, c.ingested_at;
```

| Tabla | Descripción |
|-------|-------------|
| `silver_products` | Productos limpios, precios como FLOAT, categoría normalizada |
| `silver_users` | Usuarios sin password sensible |
| `silver_carts` | Carritos normalizados (1 row por producto en carrito) |
| `silver_cart_summary` | Vista agregada por carrito (total, count, items) |

**Herramientas sugeridas:**
- **BigQuery SQL** (DDL + DML)
- **Dataflow / Dataproc** (if transformaciones más pesadas)

### Capa Gold (business aggregates)

Métricas de negocio listas para dashboards y reporting.

#### `gold_product_performance`
```sql
CREATE OR REPLACE TABLE gold_product_performance AS
SELECT
  p.category,
  p.product_id,
  p.title,
  p.price,
  COUNT(DISTINCT sc.cart_id) AS times_in_carts,
  SUM(sc.quantity) AS total_units_sold,
  SUM(p.price * sc.quantity) AS revenue,
  COUNT(DISTINCT sc.user_id) AS unique_buyers
FROM silver_products p
LEFT JOIN silver_carts sc ON p.product_id = sc.product_id
GROUP BY p.category, p.product_id, p.title, p.price;
```

#### `gold_user_behavior`
```sql
CREATE OR REPLACE TABLE gold_user_behavior AS
SELECT
  u.user_id,
  u.username,
  COUNT(DISTINCT sc.cart_id) AS total_carts,
  COUNT(DISTINCT sc.product_id) AS unique_products_purchased,
  SUM(sc.quantity) AS total_items_purchased,
  SUM(p.price * sc.quantity) AS total_spent,
  AVG(cs.total_amount) AS avg_cart_value
FROM silver_users u
LEFT JOIN silver_carts sc ON u.user_id = sc.user_id
LEFT JOIN silver_products p ON sc.product_id = p.product_id
LEFT JOIN silver_cart_summary cs ON u.user_id = cs.user_id
GROUP BY u.user_id, u.username;
```

#### `gold_category_insights`
```sql
CREATE OR REPLACE TABLE gold_category_insights AS
SELECT
  p.category,
  COUNT(DISTINCT p.product_id) AS product_count,
  ROUND(AVG(p.price), 2) AS avg_price,
  ROUND(MIN(p.price), 2) AS min_price,
  ROUND(MAX(p.price), 2) AS max_price,
  SUM(sc.quantity) AS total_units_in_carts,
  COUNT(DISTINCT sc.cart_id) AS cart_mentions
FROM silver_products p
LEFT JOIN silver_carts sc ON p.product_id = sc.product_id
GROUP BY p.category;
```

| Tabla | Descripción | Uso |
|-------|-------------|-----|
| `gold_product_performance` | Ranking de productos por ingresos, unidades, buyers únicos | Looker Studio / Tableau |
| `gold_user_behavior` | Segmentación de usuarios por gasto y frecuencia | CRM / Marketing |
| `gold_category_insights` | Resumen por categoría (precios, demanda) | Catálogo / Pricing |

**Herramientas sugeridas:**
- **BigQuery** (tablas materializadas o vistas)
- **Looker Studio** para dashboards directos desde Gold

---

## Pipeline propuesto

```
[FakeStoreAPI] ──HTTP──> [Cloud Function / Composer]
                              │
                              ▼
                    ┌──────────────────┐
                    │  Cloud Storage   │
                    │  (Bronze - raw)  │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │  BigQuery        │
                    │  (Silver - clean)│
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │  BigQuery        │
                    │  (Gold - agg)    │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │  Looker Studio   │
                    │  (Dashboards)    │
                    └──────────────────┘
```

### Orquestación
- **Cloud Scheduler** → trigger diario a Cloud Function o DAG de Composer
- **Cloud Function** Python: extrae cada endpoint, sube JSON a GCS, dispara carga a BigQuery
- **BigQuery Scheduled Queries** para transformations Silver → Gold

### Notas importantes
1. **Cart.products array**: El spec dice `Product` pero en runtime probablemente son `{ productId, quantity }`. Validar con un sample real.
2. **Auth endpoint**: `POST /auth/login` no es idempotente — no conviene ingerir masivamente. Solo registrar en logs si es necesario.
3. **Idempotencia**: Todos los GET son idempotentes; carga full-replace diaria es segura.
4. **PII**: `User.password` debe redactarse en Silver. `User.email` debe manejarse con políticas de datos sensibles.
