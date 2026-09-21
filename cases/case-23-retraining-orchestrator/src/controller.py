import concurrent.futures
import subprocess
import uuid
from pathlib import Path

STATE = Path('/shared/state.json')


def train_one(name):
    run = str(uuid.uuid4())
    subprocess.run(['python', 'train.py', '--model', name, '--out', '/shared/model.pkl'])
    return {'name': name, 'run': run, 'path': '/shared/model.pkl'}


def promote(result):
    STATE.write_text(str(result))
    Path('/shared/current').symlink_to(result['path'])


def run(names):
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        results = list(pool.map(train_one, names))
    for result in results:
        promote(result)
