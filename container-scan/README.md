# container-scan

Weekly Trivy scan of the container images used by Hosted Mender. How it runs,
where the reports go and the manual fall-back are documented in
[NorthernTechHQ/security](https://github.com/NorthernTechHQ/security/blob/main/CONTAINER-SCAN.md).

## Develop

```bash
cd container-scan
python3 -m unittest -v test_scan
docker build -t container-scan:dev .
```

## Release

Merging to master publishes
`registry.gitlab.com/northern.tech/mender/mender-test-containers/container-scan:master`.
The clusters run it pinned by digest from nt-iac `manifests/base/container-scan`:
Renovate opens the digest bump there.
