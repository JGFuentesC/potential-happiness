-- sql/silver/04_silver_cart_summary.sql
-- Denormalized cart view with totals and user info

CREATE OR REPLACE TABLE fakestore_silver.silver_cart_summary AS
SELECT
  sc.cart_id,
  sc.user_id,
  u.username,
  u.first_name,
  u.last_name,
  ARRAY_AGG(
    STRUCT(
      p.product_id,
      p.title,
      p.price,
      p.category,
      sc.quantity
    )
  ) AS items,
  SUM(p.price * sc.quantity) AS total_amount,
  COUNT(sc.product_id) AS item_count,
  sc.cart_date,
  sc._ingested_at
FROM fakestore_silver.silver_carts sc
JOIN fakestore_silver.silver_users u ON sc.user_id = u.user_id
JOIN fakestore_silver.silver_products p ON sc.product_id = p.product_id
GROUP BY sc.cart_id, sc.user_id, u.username, u.first_name, u.last_name, sc.cart_date, sc._ingested_at;
