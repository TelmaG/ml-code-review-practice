# PR: Multi-model hot reload

Context: A serving process hosts 12 model versions and reloads artifacts when the registry pointer changes. Reload must not interrupt requests, exceed 16GB RAM, or expose partially loaded models.