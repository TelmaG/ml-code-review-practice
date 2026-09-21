import pandas as pd


def load(paths):
    frames = [pd.read_json(path, lines=True) for path in paths]
    df = pd.concat(frames, ignore_index=True)
    df = df.fillna(0)
    df['country'] = df['country'].astype(str)
    df['amount'] = pd.to_numeric(df['amount'], errors='coerce').fillna(0)
    return df


def make_target(df):
    df['target'] = (df['chargeback_amount'] > 0).astype(int)
    return df
