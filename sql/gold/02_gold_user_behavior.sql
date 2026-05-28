-- sql/gold/02_gold_user_behavior.sql
-- User segmentation by spending and purchase frequency

CREATE OR REPLACE TABLE fakestore_gold.gold_user_behavior AS
SELECT
  u.user_id,
  u.username,
  u.first_name,
  u.last_name,
  u.email,
  u.city,
  COUNT(DISTINCT sc.cart_id) AS total_carts,
  COUNT(DISTINCT sc.product_id) AS unique_products_in_carts,
  COALESCE(SUM(sc.quantity), 0) AS total_items_in_carts,
  COALESCE(SUM(p.price * sc.quantity), 0) AS total_estimated_spent,
  ROUND(COALESCE(AVG(cs.total_amount), 0), 2) AS avg_cart_value,
  MAX(sc.cart_date) AS last_cart_date
FROM fakestore_silver.silver_users u
LEFT JOIN fakestore_silver.silver_carts sc ON u.user_id = sc.user_id
LEFT JOIN fakestore_silver.silver_products p ON sc.product_id = p.product_id
LEFT JOIN fakestore_silver.silver_cart_summary cs ON u.user_id = cs.user_id
GROUP BY u.user_id, u.username, u.first_name, u.last_name, u.email, u.city;
