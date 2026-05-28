-- sql/silver/03_silver_carts.sql
-- Transform bronze carts → silver carts (unnested)
-- One row per product-in-cart

CREATE OR REPLACE TABLE fakestore_silver.silver_carts AS
SELECT
  c.id AS cart_id,
  c.userId AS user_id,
  p.productId AS product_id,
  p.quantity,
  c.date AS cart_date,
  c._ingested_at
FROM fakestore_raw.raw_carts c,
UNNEST(c.products) AS p;
