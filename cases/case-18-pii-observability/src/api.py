import logging
import time
from fastapi import FastAPI
from model import predict

log = logging.getLogger()
app = FastAPI()

@app.post('/score')
def score(payload: dict):
    started = time.time()
    result = predict(payload)
    log.info('score payload=%s result=%s elapsed=%s', payload, result, time.time()-started)
    return result
