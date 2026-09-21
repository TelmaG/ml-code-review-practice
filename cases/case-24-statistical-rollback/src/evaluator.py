import requests
import numpy as np


def should_rollback(candidate, baseline):
    a = requests.get(f'https://metrics/{candidate}/scores').json()['conversion']
    b = requests.get(f'https://metrics/{baseline}/scores').json()['conversion']
    p = np.mean(a) - np.mean(b)
    latency = np.mean(requests.get(f'https://metrics/{candidate}/latency').json())
    return p < -0.01 or latency > 200
