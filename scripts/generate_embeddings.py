import json
import logging
import sys
from pathlib import Path

from google.cloud import bigquery

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

PROJECT_ID = "academia-anahuac-mtiia"
DATASET_SILVER = "fakestore_silver"
DATASET_VECTOR = "fakestore_vector"


def get_products():
    client = bigquery.Client(project=PROJECT_ID)
    query = f"""
    SELECT product_id, title, description, category, price, rating_value, rating_count, image_url
    FROM `{PROJECT_ID}.{DATASET_SILVER}.silver_products`
    ORDER BY product_id
    """
    return client.query(query).to_dataframe()


def generate_embeddings(df):
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError:
        log.info("Installing sentence-transformers...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "sentence-transformers"])
        from sentence_transformers import SentenceTransformer

    log.info("Loading model all-MiniLM-L6-v2...")
    model = SentenceTransformer("all-MiniLM-L6-v2")

    texts = (df["title"] + " " + df["description"]).tolist()
    log.info("Generating embeddings for %d products...", len(texts))

    embeddings = model.encode(texts, show_progress_bar=True)
    log.info("Embeddings shape: %s", embeddings.shape)
    return embeddings


def upload_to_bigquery(df, embeddings):
    client = bigquery.Client(project=PROJECT_ID)

    table_id = f"{PROJECT_ID}.{DATASET_VECTOR}.vector_products"

    rows = []
    for _, row in df.iterrows():
        idx = row.name
        embedding_list = embeddings[idx].tolist()
        rows.append({
            "product_id": int(row["product_id"]),
            "title": row["title"],
            "description": row["description"],
            "category": row["category"],
            "price": float(row["price"]),
            "rating_value": float(row["rating_value"]),
            "rating_count": int(row["rating_count"]),
            "image_url": row["image_url"],
            "embedding": embedding_list,
        })

    schema = [
        bigquery.SchemaField("product_id", "INTEGER"),
        bigquery.SchemaField("title", "STRING"),
        bigquery.SchemaField("description", "STRING"),
        bigquery.SchemaField("category", "STRING"),
        bigquery.SchemaField("price", "FLOAT"),
        bigquery.SchemaField("rating_value", "FLOAT"),
        bigquery.SchemaField("rating_count", "INTEGER"),
        bigquery.SchemaField("image_url", "STRING"),
        bigquery.SchemaField("embedding", "FLOAT", mode="REPEATED"),
    ]

    job_config = bigquery.LoadJobConfig(
        write_disposition="WRITE_TRUNCATE",
        schema=schema,
    )

    log.info("Uploading %d rows to %s...", len(rows), table_id)
    job = client.load_table_from_json(rows, table_id, job_config=job_config)
    job.result()
    log.info("Uploaded to %s", table_id)


def main():
    df = get_products()
    log.info("Loaded %d products from BigQuery", len(df))

    embeddings = generate_embeddings(df)

    upload_to_bigquery(df, embeddings)

    log.info("Done! Run 'make vector-index' to create the vector index")


if __name__ == "__main__":
    main()
