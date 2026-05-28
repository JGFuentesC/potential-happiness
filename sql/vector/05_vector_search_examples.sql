-- sql/vector/05_vector_search_examples.sql
-- Example vector search queries for product similarity

-- =====================================================
-- Example 1: Find similar products to a specific product
-- =====================================================
SELECT
  query.product_id AS query_product_id,
  query.title AS query_title,
  base.product_id AS similar_product_id,
  base.title AS similar_title,
  base.category AS similar_category,
  base.price AS similar_price,
  distance
FROM
  VECTOR_SEARCH(
    TABLE `fakestore_vector.vector_products`,
    'embedding',
    (SELECT embedding FROM `fakestore_vector.vector_products` WHERE product_id = 1),
    top_k => 5,
    distance_type => 'COSINE'
  )
ORDER BY distance;

-- =====================================================
-- Example 2: Find products similar to a text query
-- =====================================================
SELECT
  base.product_id,
  base.title,
  base.category,
  base.price,
  distance
FROM
  VECTOR_SEARCH(
    TABLE `fakestore_vector.vector_products`,
    'embedding',
    (SELECT ML.GENERATE_EMBEDDING(
      MODEL `fakestore_vector.text_embedding_model`,
      (SELECT 'comfortable backpack for laptop' AS content)
    ).ml_generate_embedding_result AS embedding),
    top_k => 5,
    distance_type => 'COSINE'
  )
ORDER BY distance;

-- =====================================================
-- Example 3: Find similar products within same category
-- =====================================================
WITH target_product AS (
  SELECT embedding, category
  FROM `fakestore_vector.vector_products`
  WHERE product_id = 1
)
SELECT
  base.product_id,
  base.title,
  base.category,
  base.price,
  distance
FROM
  VECTOR_SEARCH(
    TABLE `fakestore_vector.vector_products`,
    'embedding',
    (SELECT embedding FROM target_product),
    top_k => 10,
    distance_type => 'COSINE'
  )
WHERE base.category = (SELECT category FROM target_product)
ORDER BY distance
LIMIT 5;

-- =====================================================
-- Example 4: Average embedding distance between categories
-- =====================================================
SELECT
  a.category AS category_a,
  b.category AS category_b,
  AVG(ML.DISTANCE(a.embedding, b.embedding, 'COSINE')) AS avg_distance,
  COUNT(*) AS pair_count
FROM `fakestore_vector.vector_products` a
CROSS JOIN `fakestore_vector.vector_products` b
WHERE a.product_id < b.product_id
GROUP BY a.category, b.category
ORDER BY avg_distance;
