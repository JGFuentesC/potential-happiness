-- sql/vector/02_import_onnx_model.sql
-- Import ONNX sentence-transformer model into BigQuery
-- Model: all-MiniLM-L6-v2 (384 dimensions, ~80MB)
-- Runs locally in BigQuery - NO Vertex AI cost

CREATE OR REPLACE MODEL fakestore_vector.text_embedding_model
OPTIONS (
  model_type = 'ONNX',
  model_path = 'gs://fakestore-raw/models/all-MiniLM-L6-v2.onnx'
);
