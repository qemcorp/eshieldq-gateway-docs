.. _remote_access_clients:

Remote-Access Client Setup Guides
=================================

This chapter shows how to configure common VPN clients to dial in to an
eShield-Q Gateway remote-access connection. Configure the gateway side first
(:ref:`remote_access_vpn`); the examples below assume:

* Gateway address: ``vpn.example.com`` (must appear in the gateway
  certificate's Subject Alternative Name — see the note below)
* Gateway identity (``local_id`` / Remote ID on clients): ``vpn.example.com``
* An address pool attached to the connection (clients receive a virtual IP)

.. note::
   **Gateway certificate requirements for remote access.** Native clients are
   strict about the certificate the gateway presents:

   * The **SAN** must contain the exact address the client connects to
     (DNS name or IP).
   * Windows, macOS, and iOS require the **Extended Key Usage** to include
     *Server Authentication* (``serverAuth``).
   * The client must trust the **CA** that signed the gateway certificate —
     install the CA root certificate on each client device.

   Request the SAN when creating the gateway CSR (see :ref:`site_to_site`
   Step 2) and include ``serverAuth`` EKU when signing it.

To read back the settings a client needs (server address, identity,
authentication method, tunneled networks) from a saved connection, use
GET ``/api/ipsec/v1/connections/<conn_name>/client-profile``.

.. _client_windows:

Windows 11 (native IKEv2)
-------------------------

The Windows native client authenticates with **EAP-MSCHAPv2** inside IKEv2 —
use a gateway connection with **Remote Authentication** set to *EAP-RADIUS*
(recommended) or *EAP-MSCHAPv2 (local users)*.

**Step 1 — Trust the CA.** Import the CA root certificate into the **Local
Machine -> Trusted Root Certification Authorities** store (``certlm.msc``, or
``Import-Certificate`` in PowerShell).

**Step 2 — Create the connection** (PowerShell, run as Administrator):

.. code-block:: powershell

    Add-VpnConnection -Name "eShield-Q VPN" `
        -ServerAddress "vpn.example.com" `
        -TunnelType IKEv2 `
        -AuthenticationMethod Eap `
        -EncryptionLevel Maximum `
        -RememberCredential

**Step 3 — Raise the crypto settings.** Windows' built-in IKEv2 defaults are
weaker than the gateway connection's default proposals and will not
negotiate. Apply a custom IPsec policy matching the gateway defaults
(AES-256-GCM, SHA-384, ECP-384) — recommended over weakening the gateway
connection's proposals:

.. code-block:: powershell

    Set-VpnConnectionIPsecConfiguration -ConnectionName "eShield-Q VPN" `
        -EncryptionMethod GCMAES256 `
        -IntegrityCheckMethod SHA384 `
        -DHGroup ECP384 `
        -CipherTransformConstants GCMAES256 `
        -AuthenticationTransformConstants GCMAES256 `
        -PfsGroup ECP384 `
        -Force

**Step 4 — Connect.** Select the connection from the Windows network flyout
(or ``rasdial "eShield-Q VPN"``) and enter the username and password (the
RADIUS or local-user credentials). If MFA is configured on the RADIUS server,
answer the additional challenge when prompted.

.. _client_apple:

macOS and iOS (native IKEv2)
----------------------------

The native Apple client supports both username/password (EAP-MSCHAPv2, use a
gateway connection with *EAP-RADIUS* or *local users*) and **EAP-TLS** with a
client certificate.

**Manual setup (macOS System Settings -> VPN, or iOS Settings -> General ->
VPN):**

#. Add a VPN configuration of type **IKEv2**.
#. **Server** — ``vpn.example.com``
#. **Remote ID** — ``vpn.example.com`` (must match the gateway certificate's
   SAN). Leave **Local ID** empty or set it to the username.
#. **Authentication** — *Username* for EAP-MSCHAPv2, or *Certificate* for
   EAP-TLS (install the client identity as a ``.p12`` first).
#. Install and trust the CA root certificate on the device (on iOS also enable
   it under *Settings -> General -> About -> Certificate Trust Settings*).

**Managed deployment:** for fleets, distribute a ``.mobileconfig``
configuration profile (Apple Configurator or an MDM) containing the IKEv2
payload, the CA certificate, and — for EAP-TLS — the client identity. This
avoids per-device manual entry and lets you pin the exact IKE/ESP algorithms
(AES-256-GCM, SHA-384, ECP-384) in the profile.

.. _client_strongswan:

Linux (strongSwan)
------------------

With strongSwan 6.x, describe the gateway in ``/etc/swanctl/swanctl.conf``.
Place the CA root certificate in ``/etc/swanctl/x509ca/``.

**Username/password (EAP-MSCHAPv2):**

.. code-block:: text

    connections {
        eshield {
            remote_addrs = vpn.example.com
            vips = 0.0.0.0
            proposals = aes256gcm16-prfsha384-ecp384
            local {
                auth = eap-mschapv2
                eap_id = alice
            }
            remote {
                auth = pubkey
                id = vpn.example.com
            }
            children {
                eshield {
                    remote_ts = 0.0.0.0/0
                    esp_proposals = aes256gcm16-ecp384
                }
            }
        }
    }
    secrets {
        eap-alice {
            id = alice
            secret = "alice-password"
        }
    }

**Client certificate (EAP-TLS):** install the client certificate and key in
``/etc/swanctl/x509/`` and ``/etc/swanctl/private/``, then replace the
``local`` section with:

.. code-block:: text

    local {
        auth = eap-tls
        certs = alice-cert.pem
        id = alice@example.com
    }

Connect and verify:

.. code-block:: bash

    swanctl --load-all
    swanctl --initiate --child eshield
    swanctl --list-sas   # shows the SA and the assigned virtual IP

Set ``remote_ts`` to the split-tunnel networks pushed by your organisation, or
``0.0.0.0/0`` to send all traffic through the tunnel (the gateway narrows it
to the connection's traffic selectors).

.. _client_forticlient:

FortiClient
-----------

In FortiClient create a new **IPsec VPN** connection:

.. list-table::
   :header-rows: 1
   :widths: 40 60

   * - FortiClient setting
     - Value
   * - Remote Gateway
     - ``vpn.example.com``
   * - IKE Version
     - 2
   * - Authentication Method
     - Username/password (EAP) — gateway side *EAP-RADIUS*
   * - Phase 1 proposal
     - AES-256-GCM, PRF SHA-384, DH group 20 (ECP-384)
   * - Phase 2 proposal
     - AES-256-GCM, DH group 20
   * - Mode Config
     - Enabled (receives the virtual IP from the pool)

Import the CA root certificate into the client machine's trust store so the
gateway certificate validates.

.. _radius_server_examples:

RADIUS Server Examples (gateway side)
-------------------------------------

For connections using **EAP-RADIUS**, any standards-compliant RADIUS server
works. Configure the server(s) on the gateway's **VPN -> Remote Access (RADIUS)** page (see
:ref:`remote_access_radius`); on the RADIUS side register the gateway as a
client and enable EAP-MSCHAPv2.

**FreeRADIUS** — register the gateway in ``clients.conf``:

.. code-block:: text

    client eshield-gw {
        ipaddr = <gateway source IP>
        secret = <shared secret configured on the gateway>
    }

and add users (``users`` file) — ``Framed-IP-Address`` optionally pins a
static virtual IP (see :ref:`remote_access_static_ip`):

.. code-block:: text

    alice   Cleartext-Password := "alice-password"
            Framed-IP-Address = 10.66.0.200

EAP-MSCHAPv2 is enabled by default in the FreeRADIUS ``eap`` module
(``default_eap_type`` may be set to ``mschapv2``).

**Microsoft NPS (Windows Server)** — outline:

#. Register NPS in Active Directory and add a **RADIUS Client** with the
   gateway's source IP and the shared secret.
#. Create a **Network Policy** for your VPN user group with EAP type
   **Microsoft: Secured password (EAP-MSCHAP v2)**.
#. Users authenticate with their AD credentials from any of the clients above.

**MFA:** RADIUS ``Access-Challenge`` exchanges are passed through to the
client, so challenge-based MFA (for example a one-time code prompt) works with
the native clients. Enable **RADIUS Accounting** on the gateway to send
session Start/Stop records.

Troubleshooting client connections
----------------------------------

* **Client reports a certificate / policy error** — the gateway certificate's
  SAN does not contain the server address the client used, the EKU is missing
  ``serverAuth``, or the CA is not trusted on the device.
* **IKE negotiation fails immediately (Windows)** — the custom IPsec policy
  from Step 3 was not applied; Windows offered its weak defaults.
* **Authentication fails** — confirm the connection's **Remote
  Authentication** method matches what the client sends (EAP-MSCHAPv2 needs
  *EAP-RADIUS* or *local users*), and check GET ``/api/sys/v1/logs/ipsec``.
  For RADIUS, verify the shared secret and that the RADIUS server sees the
  request at all.
* **Connected but no virtual IP / no traffic** — the connection has no address
  pool attached, or the dataplane ACLs block the tunneled traffic.

More cases in :ref:`troubleshooting`.
