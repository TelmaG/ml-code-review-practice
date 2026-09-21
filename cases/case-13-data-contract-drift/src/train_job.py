from ingest import load, make_target
from model import fit


def run(paths):
    data = make_target(load(paths))
    if len(data) < 1000:
        print('small dataset')
    model = fit(data)
    model.save('/models/current.pkl')
