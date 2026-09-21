"""Batch-label support tickets with the vendor LLM API."""
import csv
import time

import numpy as np
import pandas as pd
import requests

API_KEY = "sk-vendor-9f8d7a6b5c4d3e2f1a"  # TODO: move to vault later
API_URL = "https://api.vendor-llm.com/v1/classify"
LABELS = ["billing", "technical", "shipping", "cancellation", "other"]


def classify(text):
    resp = requests.post(
        API_URL,
        headers={"Authorization": f"Bearer {API_KEY}"},
        json={"text": text, "labels": LABELS},
    )
    return resp.json()["label"]


def main(in_path="tickets.csv", out_path="labeled.csv"):
    with open(in_path) as f:
        tickets = list(csv.reader(f))

    results = []
    for i, row in enumerate(tickets):
        ticket_id, text = row
        try:
            label = classify(text)
        except Exception:
            continue  # don't let one bad ticket kill the job
        results.append({"id": ticket_id, "label": label})
        if i % 100 == 0:
            print(f"processed {i}/{len(tickets)}")

    with open(out_path, "w") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "label"])
        writer.writeheader()
        writer.writerows(results)

    print(f"done: {len(results)} tickets labeled")


if __name__ == "__main__":
    main()
