"""Fraud classifier v2 — training script."""
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from sklearn.metrics import accuracy_score, roc_auc_score
from sklearn.preprocessing import StandardScaler

FEATURES = ["amount", "hour", "merchant_age_days", "tx_count_1h",
            "country_mismatch", "card_present"]


class FraudNet(nn.Module):
    def __init__(self):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(6, 64), nn.ReLU(),
            nn.Linear(64, 32), nn.ReLU(),
            nn.Linear(32, 1), nn.Sigmoid(),
        )

    def forward(self, x):
        return self.net(x)


def main():
    df = pd.read_parquet("/data/q2_transactions.parquet")
    X = df[FEATURES]
    y = df["is_fraud"].values

    # scale features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # split into train/valid
    idx = np.random.permutation(len(X_scaled))
    cut = int(0.8 * len(idx))
    train_idx, valid_idx = idx[:cut], idx[cut:]

    X_train = torch.tensor(X_scaled[train_idx], dtype=torch.float32)
    y_train = torch.tensor(y[train_idx], dtype=torch.float32)
    X_valid = torch.tensor(X_scaled[valid_idx], dtype=torch.float32)
    y_valid = y[valid_idx]

    model = FraudNet()
    opt = torch.optim.Adam(model.parameters(), lr=0.001)
    loss_fn = nn.BCELoss()

    for epoch in range(20):
        pred = model.forward(X_train).squeeze(1)
        loss = loss_fn(pred, y_train)
        loss.backward()
        opt.step()
        print(f"epoch {epoch} loss {loss.item()}")

    # evaluate
    with torch.no_grad():
        valid_pred = model(X_valid).squeeze(1).numpy()
    print("valid accuracy:", accuracy_score(y_valid, valid_pred > 0.5))
    print("valid auc:", roc_auc_score(y_valid, valid_pred))

    torch.save(model.state_dict(), "/models/fraud/model.pt")


if __name__ == "__main__":
    main()
