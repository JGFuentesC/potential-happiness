# FakeStoreAPI Medallion Pipeline — Makefile
# Transforms: Bronze → Silver → Gold

include .env

BQ_FLAGS=--nouse_legacy_sql --project_id=$(BQ_PROJECT) --location=$(BQ_LOCATION)

.PHONY: all datasets silver gold verify clean

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
