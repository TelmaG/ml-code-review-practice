# PR: Model canary controller

Context: A new ranking model receives 5% of production traffic for one hour. The controller should compare conversion, latency, and error rate to the current model and roll back on a material regression.