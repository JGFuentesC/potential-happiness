-- sql/silver/01_silver_products.sql
-- Transform bronze products → silver products
-- Cleans, casts types, extracts rating fields

CREATE OR REPLACE TABLE fakestore_silver.silver_products AS
SELECT
  id AS product_id,
  title,
  CAST(price AS FLOAT64) AS price,
  description,
  LOWER(TRIM(category)) AS category,
  image AS image_url,
  rating.rate AS rating_value,
  rating.count AS rating_count,
  _ingested_at
FROM fakestore_raw.raw_products;
