import random
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score
from model import train


def search(df, configs):
    train_df, valid_df = train_test_split(df, test_size=.2)
    results = []
    for config in configs:
        model = train(train_df, config)
        score = roc_auc_score(valid_df.label, model.predict_proba(valid_df)[:, 1])
        results.append((score, config, model))
    best = sorted(results, reverse=True)[0]
    if best[0] > .92:
        best[2].save('/models/current.pkl')
    return best
