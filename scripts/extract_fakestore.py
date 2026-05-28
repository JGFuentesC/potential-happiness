import asyncio
import json
import logging
import sys
from pathlib import Path

import aiofiles
import aiohttp

BASE_URL = "https://fakestoreapi.com"
DATA_DIR = Path("data")
CONCURRENCY = 10
MAX_RETRIES = 2

RESOURCES = ["products", "carts", "users"]

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)


async def fetch_json(session: aiohttp.ClientSession, url: str) -> dict | list | None:
    for attempt in range(MAX_RETRIES + 1):
        try:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as resp:
                if resp.status == 200:
                    return await resp.json()
                log.warning("HTTP %s for %s (attempt %d)", resp.status, url, attempt + 1)
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            log.warning("Error fetching %s: %s (attempt %d)", url, e, attempt + 1)
        if attempt < MAX_RETRIES:
            await asyncio.sleep(1)
    log.error("Failed to fetch %s after %d attempts", url, MAX_RETRIES + 1)
    return None


async def fetch_and_save(session: aiohttp.ClientSession, resource: str, item_id: int, sem: asyncio.Semaphore, out_dir: Path):
    url = f"{BASE_URL}/{resource}/{item_id}"
    async with sem:
        data = await fetch_json(session, url)
    if data is None:
        return False
    filepath = out_dir / f"{item_id}.json"
    async with aiofiles.open(filepath, "w") as f:
        await f.write(json.dumps(data, separators=(",", ":")))
    return True


async def extract_resource(session: aiohttp.ClientSession, resource: str, sem: asyncio.Semaphore):
    log.info("Fetching %s list...", resource)
    url = f"{BASE_URL}/{resource}"
    items = await fetch_json(session, url)
    if not isinstance(items, list):
        log.error("Expected list for %s, got %s", resource, type(items).__name__)
        return

    ids = [item["id"] for item in items if "id" in item]
    log.info("Found %d %s", len(ids), resource)

    out_dir = DATA_DIR / resource
    out_dir.mkdir(parents=True, exist_ok=True)

    tasks = [fetch_and_save(session, resource, i, sem, out_dir) for i in ids]
    results = await asyncio.gather(*tasks)

    success = sum(1 for r in results if r)
    log.info("Saved %d/%d %s", success, len(ids), resource)


async def main():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    sem = asyncio.Semaphore(CONCURRENCY)
    async with aiohttp.ClientSession() as session:
        await asyncio.gather(*[extract_resource(session, r, sem) for r in RESOURCES])
    log.info("All done!")


if __name__ == "__main__":
    asyncio.run(main())
