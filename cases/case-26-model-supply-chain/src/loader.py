import hashlib
import pickle
import requests


def load(url):
    data = requests.get(url).content
    model = pickle.loads(data)
    open('/models/current.pkl', 'wb').write(data)
    return model
