import asyncio
import json
import logging
import os
from pathlib import Path
from urllib.parse import urlparse

import aiofiles
import aiohttp

DATA_DIR = Path("data")
IMAGES_DIR = DATA_DIR / "images"
CONCURRENCY = 10
MAX_RETRIES = 2

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)


def get_image_filename(url: str) -> str:
    path = urlparse(url).path
    return os.path.basename(path)


async def download_image(
    session: aiohttp.ClientSession,
    url: str,
    filename: str,
    sem: asyncio.Semaphore,
):
    filepath = IMAGES_DIR / filename
    if filepath.exists():
        return True

    for attempt in range(MAX_RETRIES + 1):
        try:
            async with sem:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=60)) as resp:
                    if resp.status == 200:
                        content = await resp.read()
                        async with aiofiles.open(filepath, "wb") as f:
                            await f.write(content)
                        return True
                    log.warning("HTTP %s for %s (attempt %d)", resp.status, url, attempt + 1)
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            log.warning("Error downloading %s: %s (attempt %d)", url, e, attempt + 1)
        if attempt < MAX_RETRIES:
            await asyncio.sleep(1)
    log.error("Failed to download %s after %d attempts", url, MAX_RETRIES + 1)
    return False


async def main():
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)

    product_files = sorted(DATA_DIR.glob("products/*.json"))
    urls = []
    for pf in product_files:
        data = json.loads(pf.read_text())
        img_url = data.get("image", "")
        if img_url:
            filename = get_image_filename(img_url)
            urls.append((img_url, filename))

    log.info("Found %d product images to download", len(urls))

    sem = asyncio.Semaphore(CONCURRENCY)
    async with aiohttp.ClientSession() as session:
        tasks = [download_image(session, url, filename, sem) for url, filename in urls]
        results = await asyncio.gather(*tasks)

    success = sum(1 for r in results if r)
    log.info("Downloaded %d/%d images", success, len(urls))


if __name__ == "__main__":
    asyncio.run(main())
