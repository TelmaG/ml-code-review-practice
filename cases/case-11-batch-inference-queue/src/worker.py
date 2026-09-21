import json
import time
import joblib
import pandas as pd
from queue_client import Queue

MODEL = '/models/risk.pkl'
queue = Queue('risk-input')


def handle(message):
    model = joblib.load(MODEL)
    rows = json.loads(message.body)
    frame = pd.DataFrame(rows)
    predictions = model.predict_proba(frame).tolist()
    queue.publish('risk-output', {'id': message.id, 'predictions': predictions})
    queue.ack(message)


def run():
    for message in queue.consume():
        try:
            handle(message)
        except Exception as exc:
            print('failed', message.id, exc)
            queue.ack(message)
        time.sleep(0.01)

if __name__ == '__main__':
    run()
