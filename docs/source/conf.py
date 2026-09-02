# Configuration file for the Sphinx documentation builder.

import re
from pathlib import Path

# -- Project information

project = "eShield-Q Gateway"
copyright = "2025, Quantum eMotion"
author = "Quantum eMotion"

# Single source with the eshieldq-gateway-docs release component, so a guide
# built into an appliance image cannot claim a version the tree does not declare.
# Read rather than imported: Sphinx does not put confdir on sys.path.
_version_text = (Path(__file__).parent / "_version.py").read_text(encoding="utf-8")


def _dunder(name: str) -> str:
    match = re.search(rf'^__{name}__\s*=\s*"([^"]+)"', _version_text, re.MULTILINE)
    if not match:
        raise RuntimeError(f"no __{name}__ assignment in docs/source/_version.py")
    return match.group(1)


# The reader is shown the appliance release (Major.Minor), never the docs
# component's own version: a banner that disagrees with the release notes reads
# as a version mismatch. The component version is still read here, so a missing
# or malformed one fails the build rather than the release.
_dunder("version")  # asserted, never displayed -- see above
release = _dunder("product_release")
version = release

# -- General configuration

extensions = [
    "sphinx.ext.duration",
    "sphinx.ext.doctest",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.intersphinx",
]

intersphinx_mapping = {
    "python": ("https://docs.python.org/3/", None),
    "sphinx": ("https://www.sphinx-doc.org/en/master/", None),
}
intersphinx_disabled_domains = ["std"]

templates_path = ["_templates"]

# Placeholder for a URL owned outside this repo (the public repositories, the
# Terraform module, PyPI). Printing a link that does not resolve reads as fact,
# so the guide prints TBD until the real value exists. Grep TBD-LINK for the sites.
rst_prolog = """
.. |TBD-LINK| replace:: *TBD*
"""

# -- Options for HTML output

html_theme = "sphinx_rtd_theme"

# -- Options for EPUB output
epub_show_urls = "footnote"
