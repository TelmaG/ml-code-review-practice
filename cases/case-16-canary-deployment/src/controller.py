import time
import requests


def evaluate(candidate, baseline):
    cand = requests.get(f'https://metrics/models/{candidate}').json()
    base = requests.get(f'https://metrics/models/{baseline}').json()
    lift = (cand['conversion'] - base['conversion']) / base['conversion']
    if lift > -0.02:
        requests.post('https://router/weights', json={'candidate': candidate, 'weight': 1.0})
        return 'promoted'
    requests.post('https://router/weights', json={'candidate': candidate, 'weight': 0.0})
    return 'rolled_back'


def run(candidate, baseline):
    time.sleep(3600)
    return evaluate(candidate, baseline)
