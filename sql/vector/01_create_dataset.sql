-- sql/vector/01_create_dataset.sql
-- Create Vector layer dataset for embeddings and vector search

CREATE SCHEMA IF NOT EXISTS fakestore_vector
OPTIONS (
  location = 'us-east4',
  description = 'Vector layer: product embeddings and vector search indexes'
);
