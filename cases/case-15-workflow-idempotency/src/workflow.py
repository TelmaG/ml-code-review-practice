import requests
import subprocess


def run(run_id, date):
    requests.get(f'https://warehouse/export?date={date}').raise_for_status()
    subprocess.run(['python', 'train.py', '--date', date])
    requests.post('https://registry/models', json={'path': '/tmp/model.pkl'})
    requests.post('https://deploy/models/current', json={'run_id': run_id})
    open('/tmp/done', 'w').write(run_id)


def retry(run_id, date):
    for attempt in range(3):
        try:
            return run(run_id, date)
        except Exception:
            continue
