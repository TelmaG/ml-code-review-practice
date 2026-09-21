# PR: Multi-GPU training launcher

Context: Four GPU workers train a ranking model on 2B examples. Runs must be reproducible enough to compare experiments. Checkpoint restart is expected after preemptions, and each worker writes logs to shared storage.