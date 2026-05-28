-- sql/vector/03_generate_embeddings.sql
-- Generate product embeddings using local ONNX model
-- Input: title + description text
-- Output: 384-dimension embedding vectors

CREATE OR REPLACE TABLE fakestore_vector.vector_products AS
SELECT
  p.product_id,
  p.title,
  p.description,
  p.category,
  p.price,
  p.rating_value,
  p.rating_count,
  p.image_url,
  embedding.ml_generate_embedding_result AS embedding,
  CURRENT_TIMESTAMP() AS _embedded_at
FROM
  ML.GENERATE_EMBEDDING(
    MODEL fakestore_vector.text_embedding_model,
    (
      SELECT
        product_id,
        CONCAT(title, ' ', description) AS content
      FROM fakestore_silver.silver_products
    )
  ) AS embedding
JOIN fakestore_silver.silver_products p
  ON embedding.product_id = p.product_id;
