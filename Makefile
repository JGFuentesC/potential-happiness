# FakeStoreAPI Medallion Pipeline — Makefile
# Transforms: Bronze → Silver → Gold → Vector

include .env

BQ_FLAGS=--nouse_legacy_sql --project_id=$(BQ_PROJECT) --location=$(BQ_LOCATION)

.PHONY: all datasets silver gold vector vector-images verify clean vector-clean notebook setup-venv download-model image-embeddings image-index

# Create Silver and Gold datasets
datasets:
	@echo "Creating datasets..."
	bq mk --dataset --location=$(BQ_LOCATION) --description="Silver layer: cleansed and structured data" $(BQ_PROJECT):$(BQ_DATASET_SILVER) 2>/dev/null || echo "  Dataset $(BQ_DATASET_SILVER) already exists"
	bq mk --dataset --location=$(BQ_LOCATION) --description="Gold layer: business aggregates" $(BQ_PROJECT):$(BQ_DATASET_GOLD) 2>/dev/null || echo "  Dataset $(BQ_DATASET_GOLD) already exists"
	@echo "Datasets ready."

# Run all Silver transformations
silver: datasets
	@echo "Running Silver layer transformations..."
	@echo "  → silver_products"
	bq query $(BQ_FLAGS) < sql/silver/01_silver_products.sql
	@echo "  → silver_users"
	bq query $(BQ_FLAGS) < sql/silver/02_silver_users.sql
	@echo "  → silver_carts"
	bq query $(BQ_FLAGS) < sql/silver/03_silver_carts.sql
	@echo "  → silver_cart_summary"
	bq query $(BQ_FLAGS) < sql/silver/04_silver_cart_summary.sql
	@echo "Silver layer complete."

# Run all Gold transformations
gold: silver
	@echo "Running Gold layer transformations..."
	@echo "  → gold_product_performance"
	bq query $(BQ_FLAGS) < sql/gold/01_gold_product_performance.sql
	@echo "  → gold_user_behavior"
	bq query $(BQ_FLAGS) < sql/gold/02_gold_user_behavior.sql
	@echo "  → gold_category_insights"
	bq query $(BQ_FLAGS) < sql/gold/03_gold_category_insights.sql
	@echo "Gold layer complete."

# Run full pipeline
all: gold
	@echo ""
	@echo "Pipeline complete. Verifying..."
	$(MAKE) verify

# Verify row counts
verify:
	@echo ""
	@echo "=== Bronze Layer ==="
	@bq query --nouse_legacy_sql --format=csv "SELECT 'raw_products' AS tbl, COUNT(*) AS cnt FROM \`$(BQ_PROJECT).$(BQ_DATASET_BRONZE).raw_products\` UNION ALL SELECT 'raw_carts', COUNT(*) FROM \`$(BQ_PROJECT).$(BQ_DATASET_BRONZE).raw_carts\` UNION ALL SELECT 'raw_users', COUNT(*) FROM \`$(BQ_PROJECT).$(BQ_DATASET_BRONZE).raw_users\`"
	@echo ""
	@echo "=== Silver Layer ==="
	@bq query --nouse_legacy_sql --format=csv "SELECT 'silver_products' AS tbl, COUNT(*) AS cnt FROM \`$(BQ_PROJECT).$(BQ_DATASET_SILVER).silver_products\` UNION ALL SELECT 'silver_users', COUNT(*) FROM \`$(BQ_PROJECT).$(BQ_DATASET_SILVER).silver_users\` UNION ALL SELECT 'silver_carts', COUNT(*) FROM \`$(BQ_PROJECT).$(BQ_DATASET_SILVER).silver_carts\` UNION ALL SELECT 'silver_cart_summary', COUNT(*) FROM \`$(BQ_PROJECT).$(BQ_DATASET_SILVER).silver_cart_summary\`"
	@echo ""
	@echo "=== Gold Layer ==="
	@bq query --nouse_legacy_sql --format=csv "SELECT 'gold_product_performance' AS tbl, COUNT(*) AS cnt FROM \`$(BQ_PROJECT).$(BQ_DATASET_GOLD).gold_product_performance\` UNION ALL SELECT 'gold_user_behavior', COUNT(*) FROM \`$(BQ_PROJECT).$(BQ_DATASET_GOLD).gold_user_behavior\` UNION ALL SELECT 'gold_category_insights', COUNT(*) FROM \`$(BQ_PROJECT).$(BQ_DATASET_GOLD).gold_category_insights\`"

# Drop Silver and Gold tables (keep Bronze)
clean:
	@echo "Dropping Silver and Gold tables..."
	bq rm -f -t $(BQ_PROJECT):$(BQ_DATASET_SILVER).silver_products 2>/dev/null || true
	bq rm -f -t $(BQ_PROJECT):$(BQ_DATASET_SILVER).silver_users 2>/dev/null || true
	bq rm -f -t $(BQ_PROJECT):$(BQ_DATASET_SILVER).silver_carts 2>/dev/null || true
	bq rm -f -t $(BQ_PROJECT):$(BQ_DATASET_SILVER).silver_cart_summary 2>/dev/null || true
	bq rm -f -t $(BQ_PROJECT):$(BQ_DATASET_GOLD).gold_product_performance 2>/dev/null || true
	bq rm -f -t $(BQ_PROJECT):$(BQ_DATASET_GOLD).gold_user_behavior 2>/dev/null || true
	bq rm -f -t $(BQ_PROJECT):$(BQ_DATASET_GOLD).gold_category_insights 2>/dev/null || true
	@echo "Clean complete."

# ============================================================
# Vector Layer Commands
# ============================================================

# Create Vector dataset
vector-dataset:
	@echo "Creating Vector dataset..."
	bq mk --dataset --location=$(BQ_LOCATION) --description="Vector layer: product embeddings and vector search" $(BQ_PROJECT):$(BQ_DATASET_VECTOR) 2>/dev/null || echo "  Dataset $(BQ_DATASET_VECTOR) already exists"

# Import ONNX model (requires model in GCS first)
vector-model: vector-dataset
	@echo "Importing ONNX model..."
	@echo "  NOTE: Upload all-MiniLM-L6-v2.onnx to gs://fakestore-raw/models/ first"
	@echo "  Download from: https://huggingface.co/optimum/all-MiniLM-L6-v2"
	bq query $(BQ_FLAGS) < sql/vector/02_import_onnx_model.sql

# Generate product text embeddings (local Python - no Vertex AI cost)
vector-embeddings: vector-dataset setup-venv
	@echo "Generating product text embeddings locally..."
	. .venv/bin/activate && python scripts/generate_embeddings.py
	@echo "Text embeddings generated."

# Generate product image embeddings (local Python - no Vertex AI cost)
image-embeddings: vector-dataset setup-venv
	@echo "Generating product image embeddings locally..."
	. .venv/bin/activate && python scripts/generate_image_embeddings.py
	@echo "Image embeddings generated."

# Create text vector index
vector-index: vector-embeddings
	@echo "Creating text vector index..."
	bq query $(BQ_FLAGS) < sql/vector/04_create_vector_index.sql
	@echo "Vector index created."

# Create image vector index
image-index: image-embeddings
	@echo "Creating image vector index..."
	bq query $(BQ_FLAGS) < sql/vector/04_create_image_vector_index.sql 2>/dev/null || echo "  SQL file not ready yet; run manually after table exists"

# Run full text vector pipeline
vector: vector-index
	@echo ""
	@echo "Vector layer (text) complete."

# Run full image vector pipeline
vector-images: image-index
	@echo ""
	@echo "Vector layer (images) complete."

# Verify vector layer
vector-verify:
	@echo ""
	@echo "=== Vector Layer ==="
	@bq query --nouse_legacy_sql --format=csv "SELECT 'vector_products' AS tbl, COUNT(*) AS cnt, AVG(ARRAY_LENGTH(embedding)) AS avg_dim FROM \`$(BQ_PROJECT).$(BQ_DATASET_VECTOR).vector_products\`"
	@echo ""
	@echo "=== Sample Embeddings ==="
	@bq query --nouse_legacy_sql --format=csv "SELECT product_id, SUBSTR(title, 1, 40) AS title, category, ROUND(price, 2) AS price FROM \`$(BQ_PROJECT).$(BQ_DATASET_VECTOR).vector_products\` LIMIT 5"

# Drop Vector tables
vector-clean:
	@echo "Dropping Vector tables..."
	bq rm -f -t $(BQ_PROJECT):$(BQ_DATASET_VECTOR).vector_products 2>/dev/null || true
	bq rm -f -m $(BQ_PROJECT):$(BQ_DATASET_VECTOR).text_embedding_model 2>/dev/null || true
	@echo "Vector clean complete."

# Open Jupyter notebook
notebook:
	@echo "Starting Jupyter..."
	. .venv/bin/activate && jupyter notebook notebooks/vector_search_visualization.ipynb

# ============================================================
# Setup Commands
# ============================================================

# Setup virtual environment with all dependencies
setup-venv:
	@echo "Setting up virtual environment..."
	uv venv .venv 2>/dev/null || echo "  .venv already exists"
	uv pip install --python .venv/bin/python \
		aiohttp aiofiles \
		google-cloud-bigquery google-cloud-storage \
		pandas scikit-learn plotly db-dtypes \
		nbformat python-dotenv ipykernel huggingface_hub \
		Pillow sentence-transformers
	@echo "Installing Jupyter kernel..."
	. .venv/bin/activate && python scripts/setup_notebook_kernel.py
	@echo "Venv ready at .venv"

# Download ONNX model and upload to GCS
download-model:
	@echo "Downloading ONNX model..."
	. .venv/bin/activate && python scripts/download_onnx_model.py
	@echo "Model uploaded to gs://fakestore-raw/models/"
