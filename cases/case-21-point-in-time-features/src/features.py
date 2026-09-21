import pandas as pd


def build(events, labels, profiles):
    events['event_ts'] = pd.to_datetime(events['event_ts'])
    labels['label_ts'] = pd.to_datetime(labels['label_ts'])
    profiles['updated_at'] = pd.to_datetime(profiles['updated_at'])
    joined = events.merge(labels, on='transaction_id')
    joined = joined.merge(profiles, on='customer_id', how='left')
    joined['rolling_7d'] = joined.groupby('customer_id')['amount'].transform(
        lambda s: s.rolling('7D').sum())
    return joined
