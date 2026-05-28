import logging
import subprocess
from pathlib import Path

import tensorflow as tf
import tensorflow_hub as hub

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S")
log = logging.getLogger(__name__)

GCS_BUCKET = "gs://fakestore-raw"
GCS_MODEL_PATH = f"{GCS_BUCKET}/models/mobilenet_v2"
LOCAL_MODEL_DIR = Path("models/mobilenet_v2_v2")


def download_model():
    log.info("Downloading MobileNetV2...")
    LOCAL_MODEL_DIR.mkdir(parents=True, exist_ok=True)

    model_url = "https://tfhub.dev/google/tf2-preview/mobilenet_v2/classification/4"
    hub_module = hub.load(model_url)

    log.info("Creating wrapper with serving signature...")

    class ModelWrapper(tf.Module):
        def __init__(self, module):
            super().__init__()
            self.module = module

        @tf.function(input_signature=[tf.TensorSpec(shape=[None, 224, 224, 3], dtype=tf.float32)])
        def __call__(self, images):
            # MobileNetV2 expects float32 in [0, 1] range
            result = self.module(images, training=False)
            return {"dense": result}

    wrapper = ModelWrapper(hub_module)

    log.info("Saving as SavedModel to %s...", LOCAL_MODEL_DIR)
    tf.saved_model.save(wrapper, str(LOCAL_MODEL_DIR))

    # Verify
    loaded = tf.saved_model.load(str(LOCAL_MODEL_DIR))
    log.info("Signatures: %s", list(loaded.signatures.keys()))

    # Test with dummy input
    sig = loaded.signatures["serving_default"]
    dummy = tf.zeros([1, 224, 224, 3], dtype=tf.float32)
    output = sig(dummy)
    log.info("Output shape: %s", output["dense"].shape)
    log.info("SavedModel saved.")


def upload_to_gcs():
    log.info("Uploading SavedModel to %s...", GCS_MODEL_PATH)
    subprocess.check_call(["gcloud", "storage", "cp", "-r", str(LOCAL_MODEL_DIR) + "/", GCS_MODEL_PATH + "/"])
    log.info("Upload complete: %s", GCS_MODEL_PATH)


def main():
    if not LOCAL_MODEL_DIR.exists() or not (LOCAL_MODEL_DIR / "saved_model.pb").exists():
        download_model()
    else:
        log.info("Model already exists at %s", LOCAL_MODEL_DIR)

    upload_to_gcs()
    log.info("Done! Model ready at %s", GCS_MODEL_PATH)


if __name__ == "__main__":
    main()
