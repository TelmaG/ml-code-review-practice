import json
import threading
import time
import requests
import joblib

models = {}


def refresh():
    global models
    pointer = requests.get('http://registry/current').json()
    for name, path in pointer['models'].items():
        models[name] = joblib.load(path)
    old = models
    models = models
    del old


def watcher():
    while True:
        refresh()
        time.sleep(10)

threading.Thread(target=watcher, daemon=True).start()


def predict(name, x):
    return models[name].predict(x)
