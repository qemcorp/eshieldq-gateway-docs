.. _site_to_site:

Site-to-Site VPN Walkthrough
============================

This walkthrough brings up an IPsec tunnel between two eShield-Q Gateways —
**GW-A** (LAN ``10.1.1.0/24``) and **GW-B** (LAN ``10.2.2.0/24``) — so hosts on
the two LANs can reach each other securely across the internet. The same steps
apply when the far end is a third-party IKEv2 peer that supports
certificate-based authentication and CNSA-strength algorithms.

Before you begin
----------------

* Both gateways are deployed and reachable (see :ref:`quick_start` steps 1–4),
  and you know each gateway's **WAN public IP** (``198.51.100.10`` for GW-A and
  ``203.0.113.20`` for GW-B in the examples below).
* Cloud network rules on both WAN interfaces allow inbound **UDP 500,
  UDP 4500, and ESP (IP protocol 50)**.
* You have (or will create) a **Certificate Authority** that both gateways
  trust. Both gateway identity certificates in this walkthrough are signed by
  the same CA.

Step 1 — Create a Certificate Authority
---------------------------------------

If you do not already operate a CA, create a root CA key and certificate on a
trusted admin workstation (not on the gateways). Example OpenSSL commands and a
ready-made configuration file are in :ref:`ca_generation`:

.. code-block:: bash

    openssl req -x509 -newkey rsa:4096 -sha384 -days 3650 \
        -keyout root_key.pem -out root_cert.pem -config openssl_root.conf

Keep ``root_key.pem`` offline and secure — only the CA *certificate*
(``root_cert.pem``) is uploaded to the gateways.

Step 2 — Issue an identity certificate to each gateway
------------------------------------------------------

Repeat on **both** gateways. The private key is generated on the gateway and
never leaves it — you only download a CSR and upload the signed certificate.

**Web UI** (PKI & Secrets -> Keys & CSRs):

#. Select **New Signing Request**. Set the **Common Name** to the gateway's
   identity (for example ``gw-a.example.com``) and include the WAN public IP
   and/or DNS name in the **IP Addresses** / **DNS Names** (SAN) fields.
#. Download the CSR from the Signing Request table and sign it with your CA
   (example commands in :ref:`cert_signing`).
#. In the Signing Request table select **Actions -> Upload Signed
   Certificate**, choose the signed certificate, and set **usage** to
   ``IPSEC``.
#. Upload the CA root certificate on **PKI & Secrets -> Certificates** so
   the gateway can validate its peer.

**REST API**:

* Create the CSR: POST ``/api/certs/v1/signing_request``
* Upload the signed certificate: POST ``/api/certs/v1/signed_csr``
  (``usage: IPSEC``)
* Upload the CA certificate: POST ``/api/certs/v1/ca``
* Verify: GET ``/api/certs/v1/all`` and GET ``/api/certs/v1/details``

Step 3 — Permit IPsec traffic in the dataplane ACLs
---------------------------------------------------

On both gateways add WAN rules permitting UDP 500/4500 and ESP, and LAN rules
permitting the traffic you intend to tunnel (or start with permit-all on the
LAN and tighten later). See :ref:`setup_acl_rules`; ready-made examples are in
:ref:`example_acl_rules`.

Step 4 — Create the connection on both gateways
-----------------------------------------------

Create the connection on the Web UI **VPN -> Connections** page
(**Add Connection**). The two configurations mirror each other:

.. list-table::
   :header-rows: 1
   :widths: 30 35 35

   * - Field
     - GW-A
     - GW-B
   * - Name
     - ``to-gw-b``
     - ``to-gw-a``
   * - Remote Gateway (``remote_host``)
     - ``203.0.113.20``
     - ``198.51.100.10``
   * - Local ID
     - ``gw-a.example.com``
     - ``gw-b.example.com``
   * - Remote ID
     - ``gw-b.example.com``
     - ``gw-a.example.com``
   * - Local Certificate
     - GW-A's IPsec certificate
     - GW-B's IPsec certificate
   * - CA Certificate
     - the shared root CA
     - the shared root CA
   * - Local Traffic Selector
     - ``10.1.1.0/24``
     - ``10.2.2.0/24``
   * - Remote Traffic Selector
     - ``10.2.2.0/24``
     - ``10.1.1.0/24``

The defaults are the recommended CNSA-strength settings — IKEv2, AES-256-GCM,
ECP-384, PRF-SHA-384, MOBIKE, IKE fragmentation, and DPD — so the remaining
fields can normally be left as-is. For third-party peers that cannot meet
these, other algorithms can be selected per connection (AES-128/192 GCM or
CBC, SHA-256/512, ECP-256/521, Curve25519, MODP-2048/3072/4096).

**REST API** — the equivalent connection upload on GW-A
(POST ``/api/ipsec/v1/connections``):

.. code-block:: json

    {
      "name": "to-gw-b",
      "local_host": "198.51.100.10",
      "remote_host": "203.0.113.20",
      "local_id": "gw-a.example.com",
      "remote_id": "gw-b.example.com",
      "child_sas": [
        {
          "name": "lan-to-lan",
          "local_ts": ["10.1.1.0/24"],
          "remote_ts": ["10.2.2.0/24"],
          "start_action": "start"
        }
      ]
    }

Unspecified fields take the secure defaults (IKEv2, AES-256-GCM/ECP-384 IKE
and ESP proposals, tunnel mode). Select the uploaded local certificate and CA
with ``local_cert_fingerprint`` and ``local_cacerts``/``remote_cacerts``
(fingerprints from GET ``/api/certs/v1/all``).

Step 5 — Activate the connection
--------------------------------

Activate on both gateways from **VPN -> Connections -> Actions ->
Activate**, or with the REST API:

* Activate: POST ``/api/ipsec/v1/connections/loaded/<conn_name>``
* If the tunnel does not start on its own, force initiation from the
  **Active Sessions** page or POST ``/api/ipsec/v1/sas/initiate-child``

Step 6 — Verify
---------------

* **VPN -> Active Sessions** on either gateway shows the IKE SA
  *ESTABLISHED* with the child SA installed:

.. image:: images/UI/IPsec_Active_Sessions.png
    :align: center
    :scale: 50%

|

* Ping from a host on ``10.1.1.0/24`` to a host on ``10.2.2.0/24``.
* **Monitoring -> IPsec** byte/packet counters increase while traffic flows.
* REST API: GET ``/api/ipsec/v1/sas`` shows the SA state and traffic counters.

Optional — Post-quantum key exchange
------------------------------------

To harden the tunnel against future quantum attacks, edit the connection on
**both** ends and either:

* add **ML-KEM** (``mlkem1024``) as an additional key-exchange method, or
* configure a **Postquantum Preshared Key (PPK)** shared by both gateways.

Both options are described in :ref:`post_quantum_safe_mlkem`.

If it fails
-----------

* **No response from peer** — check the cloud network rules and WAN ACLs
  (UDP 500/4500, ESP) on both sides; confirm the WAN public IPs.
* **Authentication failed** — the peer's certificate must chain to the CA you
  uploaded, and the configured **Remote ID** must match the peer certificate's
  subject/SAN. Check GET ``/api/sys/v1/logs/ipsec``.
* **Tunnel up but no traffic** — traffic selectors must mirror each other, and
  the LAN ACLs must permit the tunneled traffic; check ACL deny counters in
  **Monitoring -> System Counters (Errors)**.

More cases in :ref:`troubleshooting`.
