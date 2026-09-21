import threading
import time
import pandas as pd
import requests

FEATURES = {}
LAST_REFRESH = 0


def refresh():
    global FEATURES, LAST_REFRESH
    data = requests.get('https://warehouse.internal/features').json()
    FEATURES = data
    LAST_REFRESH = time.time()


def get(user_id):
    if time.time() - LAST_REFRESH > 300:
        threading.Thread(target=refresh).start()
    return FEATURES.get(str(user_id), {'risk': 0.5})


def warmup():
    df = pd.read_parquet('/data/features.parquet')
    for row in df.to_dict('records'):
        FEATURES[str(row['user_id'])] = row
