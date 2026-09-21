import logging
import threading
import time
from types import MappingProxyType

import joblib
import requests

log = logging.getLogger('model-registry')
_models = MappingProxyType({})
_lock = threading.Lock()
_generation = None


def refresh(pointer_url: str) -> bool:
    response = requests.get(pointer_url, timeout=(1, 5))
    response.raise_for_status()
    pointer = response.json()
    candidate = {}
    for name, spec in pointer['models'].items():
        model = joblib.load(spec['path'])
        if spec.get('version') != getattr(model, 'version', spec.get('version')):
            raise ValueError(f'incompatible artifact for {name}')
        candidate[name] = model
    global _models, _generation
    with _lock:
        _models = MappingProxyType(candidate)
        _generation = pointer['generation']
    log.info('model generation installed', extra={'generation': _generation})
    return True


def predict(name, x):
    snapshot = _models
    return snapshot[name].predict(x)
