-- sql/gold/01_gold_product_performance.sql
-- Product ranking by revenue, units, and unique buyers

CREATE OR REPLACE TABLE fakestore_gold.gold_product_performance AS
SELECT
  p.category,
  p.product_id,
  p.title,
  p.price,
  p.rating_value,
  p.rating_count,
  COUNT(DISTINCT sc.cart_id) AS times_in_carts,
  COALESCE(SUM(sc.quantity), 0) AS total_units_in_carts,
  COALESCE(SUM(p.price * sc.quantity), 0) AS estimated_revenue,
  COUNT(DISTINCT sc.user_id) AS unique_buyers
FROM fakestore_silver.silver_products p
LEFT JOIN fakestore_silver.silver_carts sc ON p.product_id = sc.product_id
GROUP BY p.category, p.product_id, p.title, p.price, p.rating_value, p.rating_count;
