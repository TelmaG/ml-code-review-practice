import pandas as pd


def choose_threshold(df):
    df = df.dropna(subset=['score', 'label'])
    threshold = (df.score > .5)
    by_group = df.groupby('group').apply(lambda x: (x.score > .5).mean())
    print(by_group)
    return .5
