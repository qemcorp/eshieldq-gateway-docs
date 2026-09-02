# eShield-Q Gateway — User Guide

Sphinx sources for the eShield-Q Gateway user documentation: deployment on AWS,
Azure and Google Cloud, network and firewall configuration, site-to-site and
remote-access VPN, certificates, monitoring and troubleshooting.

The same guide is built into the appliance image and served at `/docs/`, where
it always matches the installed firmware.

## Build it locally

```bash
cd docs
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/sphinx-build -b html source build/html
python3 -m http.server 8899 -d build/html
```

The build must complete with **zero warnings** — a broken cross-reference or a
missing image is reported as a warning, and the published build treats warnings
as errors.

## Contributing

Corrections and clarifications are welcome. Please open a pull request against
`docs/source/`. Screenshots are produced by an automated capture pipeline
rather than taken by hand, so please describe the change you would like rather
than attaching a replacement image.

Version **4.0.10**. See [SECURITY.md](SECURITY.md) to report a vulnerability.

© Quantum eMotion Corp. See [LICENSE.md](LICENSE.md).
