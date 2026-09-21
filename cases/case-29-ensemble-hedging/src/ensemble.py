import concurrent.futures
import requests

MODELS = ['a', 'b', 'c']

def score(payload):
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        futures = [pool.submit(requests.post, f'http://{m}/score', json=payload) for m in MODELS]
        results = [f.result().json()['score'] for f in futures]
    return sum(results) / len(results)
