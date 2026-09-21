# Answer key

## P1
1. Arbitrary URL and unauthenticated download allow SSRF/data exfiltration and loading attacker-controlled artifacts.
2. `pickle.loads` is code execution on untrusted bytes; artifact must be authenticated/signed and allowlisted before deserialization.
3. No checksum/signature/version verification and writes directly to current path; partial download or tampering can replace production.

## P2
4. No timeout/size limit; a large or hanging response can exhaust deploy workers.
5. Non-atomic write and no file permissions/rollback.
6. No provenance metadata or compatibility check for Python/framework/model schema.
