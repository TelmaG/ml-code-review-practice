# PR: Historical feature builder

Context: Fraud labels are generated after the transaction. Training examples must use only features available at prediction time. Data is 2B events, partitioned by event date, and the model is evaluated on a future month.