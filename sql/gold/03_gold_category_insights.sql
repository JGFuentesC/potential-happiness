-- sql/gold/03_gold_category_insights.sql
-- Category-level pricing and demand summary

CREATE OR REPLACE TABLE fakestore_gold.gold_category_insights AS
SELECT
  p.category,
  COUNT(DISTINCT p.product_id) AS product_count,
  ROUND(AVG(p.price), 2) AS avg_price,
  ROUND(MIN(p.price), 2) AS min_price,
  ROUND(MAX(p.price), 2) AS max_price,
  ROUND(AVG(p.rating_value), 2) AS avg_rating,
  SUM(p.rating_count) AS total_rating_votes,
  COALESCE(SUM(sc.quantity), 0) AS total_units_in_carts,
  COUNT(DISTINCT sc.cart_id) AS cart_mentions,
  COUNT(DISTINCT sc.user_id) AS unique_users_interested
FROM fakestore_silver.silver_products p
LEFT JOIN fakestore_silver.silver_carts sc ON p.product_id = sc.product_id
GROUP BY p.category;
