> **[P1] loader.py:7 — untrusted URL and pickle load.** A caller-controlled URL can return a payload that executes during `pickle.loads`. Use an allowlisted artifact reference, authenticated object-store access, signature verification, and a safe serialization format where possible.

> **[P1] no integrity check and direct current-path write.** A partial/tampered download can become the production artifact. Verify digest/signature, write to a versioned temporary file, fsync/atomic-rename, and publish a manifest pointer.

> **[P2] no timeout or size bound.** A hung/huge response can block deployment; add connect/read timeout and content-length/stream limits.
