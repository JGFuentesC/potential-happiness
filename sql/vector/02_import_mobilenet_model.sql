-- sql/vector/02_import_mobilenet_model.sql
-- Import MobileNetV2 TensorFlow model for image embeddings
-- Model: mobilenet_v2 feature vector (1280 dimensions)
-- Runs locally in BigQuery - NO Vertex AI cost

CREATE OR REPLACE MODEL fakestore_vector.image_embedding_model
OPTIONS (
  model_type = 'TENSORFLOW',
  model_path = 'gs://fakestore-raw/models/mobilenet_v2/mobilenet_v2/*'
);
