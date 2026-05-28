import logging
import subprocess
import sys
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

MODEL_REPO = "optimum/all-MiniLM-L6-v2"
MODEL_FILE = "model.onnx"
GCS_BUCKET = "gs://fakestore-raw"
GCS_MODEL_PATH = f"{GCS_BUCKET}/models/all-MiniLM-L6-v2.onnx"
LOCAL_MODEL_DIR = Path("models")
LOCAL_MODEL_PATH = LOCAL_MODEL_DIR / "all-MiniLM-L6-v2.onnx"


def download_model():
    log.info("Downloading ONNX model from Hugging Face: %s", MODEL_REPO)
    LOCAL_MODEL_DIR.mkdir(parents=True, exist_ok=True)

    try:
        from huggingface_hub import hf_hub_download
    except ImportError:
        log.info("Installing huggingface_hub...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "huggingface_hub"])
        from huggingface_hub import hf_hub_download

    downloaded = hf_hub_download(
        repo_id=MODEL_REPO,
        filename=MODEL_FILE,
        local_dir=LOCAL_MODEL_DIR,
        local_dir_use_symlinks=False,
    )

    if Path(downloaded).name != "all-MiniLM-L6-v2.onnx":
        target = LOCAL_MODEL_PATH
        Path(downloaded).rename(target)
        log.info("Renamed to %s", target)
    else:
        log.info("Downloaded to %s", downloaded)

    return LOCAL_MODEL_PATH


def upload_to_gcs(local_path: Path):
    log.info("Uploading to %s", GCS_MODEL_PATH)
    subprocess.check_call(["gcloud", "storage", "cp", str(local_path), GCS_MODEL_PATH])
    log.info("Upload complete: %s", GCS_MODEL_PATH)


def verify_gcs():
    result = subprocess.run(
        ["gcloud", "storage", "ls", f"{GCS_BUCKET}/models/"],
        capture_output=True, text=True
    )
    if GCS_MODEL_PATH in result.stdout:
        log.info("Verified: model exists in GCS")
        return True
    log.error("Model not found in GCS")
    return False


def main():
    if not LOCAL_MODEL_PATH.exists():
        download_model()
    else:
        log.info("Model already downloaded: %s", LOCAL_MODEL_PATH)

    upload_to_gcs(LOCAL_MODEL_PATH)
    verify_gcs()

    log.info("Done! Model ready at %s", GCS_MODEL_PATH)
    log.info("You can now run: make vector")


if __name__ == "__main__":
    main()
