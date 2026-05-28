-- sql/vector/04_create_vector_index.sql
-- Create vector index for fast similarity search
-- Index type: IVF (Inverted File) for small-medium datasets

CREATE OR REPLACE VECTOR INDEX fakestore_vector.product_embedding_index
ON fakestore_vector.vector_products(embedding)
OPTIONS (
  index_type = 'IVF',
  distance_type = 'COSINE',
  ivf_options = '{"num_lists": 4}'
);
