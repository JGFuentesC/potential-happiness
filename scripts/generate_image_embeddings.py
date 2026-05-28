import io
import logging
import re
import sys

from google.cloud import bigquery
from google.cloud import storage

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

PROJECT_ID = "academia-anahuac-mtiia"
DATASET_SILVER = "fakestore_silver"
DATASET_VECTOR = "fakestore_vector"
GCS_BUCKET = "fakestore-raw"
GCS_IMAGES_PREFIX = "images/"


def get_products():
    client = bigquery.Client(project=PROJECT_ID)
    query = f"""
    SELECT product_id, title, description, category, price, rating_value, rating_count, image_url
    FROM `{PROJECT_ID}.{DATASET_SILVER}.silver_products`
    ORDER BY product_id
    """
    return client.query(query).to_dataframe()


def load_and_preprocess_images(df):
    try:
        from PIL import Image
    except ImportError:
        log.info("Installing Pillow...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "Pillow"])
        from PIL import Image

    storage_client = storage.Client(project=PROJECT_ID)
    bucket = storage_client.bucket(GCS_BUCKET)

    images = []
    for _, row in df.iterrows():
        filename = re.search(r"([^/]+)$", row["image_url"]).group(1)
        gcs_uri = f"gs://{GCS_BUCKET}/{GCS_IMAGES_PREFIX}{filename}"
        log.info("Downloading image %d from %s", row["product_id"], gcs_uri)
        blob = bucket.blob(f"{GCS_IMAGES_PREFIX}{filename}")
        img_bytes = blob.download_as_bytes()
        img = Image.open(io.BytesIO(img_bytes))
        if img.mode != "RGB":
            img = img.convert("RGB")
        images.append(img)
    return images


def generate_embeddings(images):
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError:
        log.info("Installing sentence-transformers...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "sentence-transformers"])
        from sentence_transformers import SentenceTransformer

    log.info("Loading CLIP model (clip-ViT-B-32)...")
    model = SentenceTransformer("clip-ViT-B-32")

    log.info("Generating image embeddings for %d products...", len(images))
    embeddings = model.encode(images, show_progress_bar=True)
    log.info("Embeddings shape: %s", embeddings.shape)
    return embeddings


def upload_to_bigquery(df, embeddings):
    client = bigquery.Client(project=PROJECT_ID)

    table_id = f"{PROJECT_ID}.{DATASET_VECTOR}.image_products"

    rows = []
    for idx, (_, row) in enumerate(df.iterrows()):
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

    images = load_and_preprocess_images(df)
    embeddings = generate_embeddings(images)

    upload_to_bigquery(df, embeddings)

    log.info("Done! Image embeddings in %s.image_products", DATASET_VECTOR)
    log.info("Next: create vector index and run similarity search queries")


if __name__ == "__main__":
    main()
