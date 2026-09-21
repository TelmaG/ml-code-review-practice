# PR: GPU inference endpoint

Context: 1,500 requests/sec, p99 under 80ms. Requests contain 1–32 images. One 24GB GPU serves the model; CPU preprocessing is expected to overlap with inference.