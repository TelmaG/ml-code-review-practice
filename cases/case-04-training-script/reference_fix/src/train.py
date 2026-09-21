"""Fraud classifier v2 — reference fix."""
import json
import os
import random
from datetime import date

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from sklearn.metrics import average_precision_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

SEED = 42
FEATURES = ["amount", "hour", "merchant_age_days", "tx_count_1h",
            "country_mismatch", "card_present"]


def set_seeds(seed: int = SEED) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False


class FraudNet(nn.Module):
    def __init__(self):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(6, 64), nn.ReLU(), nn.Dropout(0.2),
            nn.Linear(64, 32), nn.ReLU(),
            nn.Linear(32, 1),
        )

    def forward(self, x):
        return self.net(x).squeeze(1)


def main():
    set_seeds()
    device = "cuda" if torch.cuda.is_available() else "cpu"

    df = pd.read_parquet(os.environ["TRAIN_PARQUET"])
    X = df[FEATURES].to_numpy(dtype="float32")
    y = df["is_fraud"].to_numpy(dtype="float32")

    # split BEFORE any fitting — no leakage
    X_train, X_valid, y_train, y_valid = train_test_split(
        X, y, test_size=0.2, random_state=SEED, stratify=y
    )

    scaler = StandardScaler().fit(X_train)   # fit on train ONLY
    X_train, X_valid = scaler.transform(X_train), scaler.transform(X_valid)

    X_train_t = torch.tensor(X_train).to(device)
    y_train_t = torch.tensor(y_train).to(device)
    X_valid_t = torch.tensor(X_valid).to(device)

    model = FraudNet().to(device)
    opt = torch.optim.Adam(model.parameters(), lr=1e-3)
    # 1% positives: weight the loss instead of pretending accuracy matters
    pos_weight = torch.tensor([(y_train == 0).sum() / max((y_train == 1).sum(), 1)]).to(device)
    loss_fn = nn.BCEWithLogitsLoss(pos_weight=pos_weight)

    n_epochs, batch_size = 30, 4096
    best_auc, best_state = 0.0, None

    for epoch in range(n_epochs):
        model.train()
        perm = torch.randperm(len(X_train_t))  # mini-batches, shuffled per epoch
        for i in range(0, len(perm), batch_size):
            b = perm[i:i + batch_size]
            opt.zero_grad()                    # grads must not accumulate
            loss = loss_fn(model(X_train_t[b]), y_train_t[b])
            loss.backward()
            opt.step()

        model.eval()
        with torch.no_grad():
            valid_logits = model(X_valid_t).cpu().numpy()
        auc = roc_auc_score(y_valid, 1 / (1 + np.exp(-valid_logits)))
        pr_auc = average_precision_score(y_valid, 1 / (1 + np.exp(-valid_logits)))
        print(f"epoch {epoch}: valid AUC={auc:.4f} PR-AUC={pr_auc:.4f}")
        if auc > best_auc:  # checkpoint the BEST epoch, not the last
            best_auc = auc
            best_state = {k: v.cpu().clone() for k, v in model.state_dict().items()}

    # versioned artifact + metadata; promotion is a separate explicit step
    version = date.today().isoformat()
    out_dir = f"/models/fraud/{version}"
    os.makedirs(out_dir, exist_ok=True)
    torch.save(best_state, f"{out_dir}/model.pt")
    import joblib
    joblib.dump(scaler, f"{out_dir}/scaler.joblib")  # prevent train/serve skew
    with open(f"{out_dir}/metadata.json", "w") as f:
        json.dump({"seed": SEED, "valid_auc": best_auc, "features": FEATURES}, f)
    print(f"saved {out_dir} (valid AUC={best_auc:.4f}) — promote explicitly if approved")


if __name__ == "__main__":
    main()
