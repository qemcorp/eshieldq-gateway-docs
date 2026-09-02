"""Versions of the user documentation set.

``__version__`` is the documentation component's own release, read by conf.py
and by the release tooling so the guide cannot claim a version the tree does not
declare. Roll it whenever the documented behaviour changes.

``__product_release__`` is the appliance release the guide documents, and is
what the rendered guide shows the reader. It is Major.Minor only: the reader is
told which product release this is, not which documentation build produced it.
Roll it when the appliance's release changes.
"""

__version__ = "4.0.10"
__product_release__ = "3.1"
