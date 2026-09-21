import os
import requests
from fastapi import FastAPI

app = FastAPI()
KEY = os.environ['API_KEY']

@app.post('/complete')
def complete(payload: dict):
    tenant = payload['tenant']
    prompt = payload['prompt']
    response = requests.post('https://llm.vendor/v1/chat', headers={'Authorization': KEY},
                             json={'prompt': prompt})
    body = response.json()
    return {'tenant': tenant, 'text': body.get('text', ''), 'usage': body.get('usage', {})}
