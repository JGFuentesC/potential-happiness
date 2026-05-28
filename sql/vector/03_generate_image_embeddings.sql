-- sql/vector/03_generate_image_embeddings.sql
-- Generate product image embeddings using MobileNetV2
-- Input: product images from GCS
-- Output: 1280-dimension embedding vectors

-- Step 1: Create a table with product image URIs
CREATE OR REPLACE TABLE fakestore_vector.product_images AS
SELECT
  p.product_id,
  p.title,
  p.description,
  p.category,
  p.price,
  p.rating_value,
  p.rating_count,
  p.image_url,
  CONCAT('gs://fakestore-raw/images/', REGEXP_EXTRACT(p.image_url, r'[^/]+$')) AS image_gcs_uri
FROM fakestore_silver.silver_products p;

-- Step 2: Generate embeddings using MobileNetV2 model
CREATE OR REPLACE TABLE fakestore_vector.vector_products AS
SELECT
  product_id,
  title,
  description,
  category,
  price,
  rating_value,
  rating_count,
  image_url,
  image_gcs_uri,
  embedding AS embedding,
  CURRENT_TIMESTAMP() AS _embedded_at
FROM
  ML.PREDICT(
    MODEL fakestore_vector.image_embedding_model,
    (
      SELECT
        product_id,
        title,
        description,
        category,
        price,
        rating_value,
        rating_count,
        image_url,
        image_gcs_uri,
        image_gcs_uri AS content
      FROM fakestore_vector.product_images
    )
  );
