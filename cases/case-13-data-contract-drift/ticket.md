# PR: Training data ingestion

Context: Daily events come from six producers. The classifier retrains at 04:00 and consumes 30M rows. Producers may add columns or change nullability without coordinating. The model must fail before training on a broken contract.