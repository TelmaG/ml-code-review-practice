"""Batch-label support tickets — reference fix."""
import asyncio
import csv
import logging
import os

import aiohttp
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_random_exponential,
)

API_KEY = os.environ["VENDOR_API_KEY"]  # never in source; rotate the leaked one
API_URL = "https://api.vendor-llm.com/v1/classify"
LABELS = ["billing", "technical", "shipping", "cancellation", "other"]
MAX_CONCURRENCY = 12          # under the 20 req/s vendor limit, with headroom
REQUEST_TIMEOUT = aiohttp.ClientTimeout(total=30, connect=5)
MAX_FAILURE_RATE = 0.01

logger = logging.getLogger("labeler")


class TransientError(Exception):
    pass


@retry(
    retry=retry_if_exception_type(TransientError),
    wait=wait_random_exponential(multiplier=1, max=60),  # backoff + jitter
    stop=stop_after_attempt(5),
)
async def classify(session: aiohttp.ClientSession, sem: asyncio.Semaphore, text: str) -> str:
    async with sem:
        async with session.post(
            API_URL,
            headers={"Authorization": f"Bearer {API_KEY}"},
            json={"text": text, "labels": LABELS},
            timeout=REQUEST_TIMEOUT,
        ) as resp:
            if resp.status in (429, 500, 502, 503, 504):
                raise TransientError(f"status {resp.status}")  # retryable
            resp.raise_for_status()  # 4xx other than 429 = fail fast, don't retry
            body = await resp.json()
    label = body.get("label")
    if label not in LABELS:
        raise ValueError(f"unexpected label payload: {body!r}")  # loud, not silent
    return label


async def run(tickets: list[tuple[str, str]], out_path: str) -> None:
    done_ids = set()
    if os.path.exists(out_path):  # resume: skip already-labeled tickets
        with open(out_path) as f:
            done_ids = {r["id"] for r in csv.DictReader(f)}
    pending = [(i, t) for i, t in tickets if i not in done_ids]

    sem = asyncio.Semaphore(MAX_CONCURRENCY)
    failures = 0
    async with aiohttp.ClientSession() as session:
        with open(out_path, "a", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["id", "label"])
            if not done_ids:
                writer.writeheader()

            async def one(ticket_id: str, text: str):
                nonlocal failures
                try:
                    label = await classify(session, sem, text)
                except Exception:
                    failures += 1
                    logger.exception("failed ticket", extra={"ticket_id": ticket_id})
                    return
                writer.writerow({"id": ticket_id, "label": label})
                f.flush()  # incremental checkpoint

            await asyncio.gather(*(one(i, t) for i, t in pending))

    failure_rate = failures / max(len(pending), 1)
    logger.info("done", extra={"labeled": len(pending) - failures,
                               "failures": failures, "failure_rate": failure_rate})
    if failure_rate > MAX_FAILURE_RATE:
        raise SystemExit(f"failure rate {failure_rate:.1%} > {MAX_FAILURE_RATE:.0%} — "
                         f"results are incomplete, rerun to fill gaps")


def main(in_path: str = "tickets.csv", out_path: str = "labeled.csv") -> None:
    with open(in_path) as f:
        tickets = [(r[0], r[1]) for r in csv.reader(f)]
    asyncio.run(run(tickets, out_path))


if __name__ == "__main__":
    main()
