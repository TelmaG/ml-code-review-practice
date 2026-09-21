# Reference fix — project skeleton for case 06

```
demand-forecast/
├── README.md                 # what it does, how to run, where data lives
├── requirements.txt          # pinned
├── Makefile                  # make setup / test / train
├── .gitignore                # data/, models/, .env, __pycache__
├── .github/workflows/ci.yml  # lint + test on PR
├── src/
│   └── train.py              # functions + CLI entrypoint, seeded split
├── tests/
│   └── test_train.py         # smoke test on a small fixture
└── data/                     # NOT in git — pulled via DVC
```

See `reference_fix/src/` for the reorganized code.
