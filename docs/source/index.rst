Welcome to eShield-Q Gateway's documentation!
==============================================

**eShield-Q Gateway** is a Point-to-Point IPsec VPN and Firewall with advanced security and performance.
The eShield-Q Gateway uses the patent pending `SecureKey Cryptographic Library <https://www.quantumemotion.com/>`_ to protect keys and secure networks.

The python client SDK and API Schema will be published by Quantum eMotion
(|TBD-LINK|) and on PyPI (|TBD-LINK|).
Once published, the python client module is installed by running:

.. code-block:: bash

   pip install eshieldq-gateway-client

eShield-Q Gateway is available for the following cloud providers:

* :ref:`Azure Cloud <azure_overview>`
* :ref:`Google Cloud <google_overview>`
* :ref:`AWS Cloud <aws_overview>`


Contents
--------

.. toctree::
   :caption: Get Started

   overview
   quick_start
   getting_started

.. toctree::
   :caption: Deploy

   azure
   google
   aws

.. toctree::
   :caption: Administer

   user_management
   security_config
   updates
   device_license
   common_operations

.. toctree::
   :caption: Network & Firewall

   network
   access_control_lists

.. toctree::
   :caption: VPN

   site_to_site
   ipsec
   remote_access
   directory_auth
   remote_access_clients
   certificates

.. toctree::
   :caption: Monitor & Troubleshoot

   system_monitor
   statistics
   troubleshooting
   faq

.. toctree::
   :caption: Reference

   api
   release_notes
   license
