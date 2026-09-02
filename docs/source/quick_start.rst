.. _quick_start:

Quick Start
===========

This chapter takes a new eShield-Q Gateway from first boot to a working,
secured deployment. Each step links to the detailed chapter for that topic.

What you will need:

* An eShield-Q Gateway VM deployed in your cloud (see Step 1).
* The cloud **Instance ID** of the VM (shown in your cloud console) — required
  to create the initial administrator.
* A browser that can reach the management interface over HTTPS.

Step 1 — Deploy the VM
----------------------

Deploy the gateway from your cloud marketplace with three network interfaces —
MGMT, WAN, and LAN. Follow the guide for your cloud:

* :ref:`Azure <install_azure>`
* :ref:`Google Cloud <google_overview>`
* :ref:`AWS <install_aws>`

.. note::
   Two sets of "firewall" rules affect the gateway:

   #. **Cloud network rules** (Azure NSG / AWS-GCP security groups or firewall
      rules) — the management interface needs inbound TCP 443 (HTTPS) and
      TCP 22 (SSH); the WAN interface needs inbound **UDP 500, UDP 4500, and
      IP protocol 50 (ESP)** for IPsec.
   #. The gateway's own **dataplane ACLs**, which default to **deny-all**
      (Step 5).

Step 2 — Create the initial administrator
-----------------------------------------

Browse to ``https://<management_ip_address>/``. Because no users exist yet,
enter any character in the username and password fields and select **Login** —
the initial-user form opens. Provide the administrator username, a password
(14+ characters), and the VM's **Instance ID**:

.. image:: images/UI/Initial_User_Create_v2.png
    :align: center
    :scale: 50%

|

See :ref:`initial_user` for the REST API and CLI variants.

Step 3 — Log in and set the security policy
-------------------------------------------

Log in as the administrator, then review the system security policy on
**System -> Security**: enable **OTP enforcement** so all users require MFA,
and confirm the token and password timeouts fit your policy. Enable MFA for
your own account under **My Account -> One-Time Password** before enforcing it globally.

See :ref:`security_policy` and :ref:`user_management`.

Step 4 — Verify system status and interface roles
-------------------------------------------------

On **System -> Status & Health**, confirm all sub-systems (dataplane, IKE daemon, HTTPS,
SSH) are healthy. On **Network -> Interfaces**, confirm the WAN and LAN roles
were assigned to the intended interfaces — roles are inferred from the IP
addressing at first boot and can be re-assigned (reboot required).

See :ref:`network_setup`.

Step 5 — Open the firewall (dataplane ACLs)
-------------------------------------------

.. warning::
   A new gateway passes **no dataplane traffic**: the default ACL policy is
   deny-all on both LAN and WAN. Until you add permit rules, IPsec peers cannot
   reach the gateway and LAN hosts cannot send traffic through it. This does
   not affect the management interface.

At minimum, permit IKE and ESP on the WAN interface (UDP 500/4500 and protocol
ESP) and permit your internal traffic on the LAN interface. See
:ref:`setup_acl_rules` for UI steps and :ref:`example_acl_rules` for ready-made
rule sets.

Step 6 — Install certificates
-----------------------------

The gateway authenticates IKE peers with certificates (or EAP for remote
access) — pre-shared keys are not supported. Generate a CSR on the gateway, sign it with your CA, and upload the
signed certificate with usage ``IPSEC``. While you are at it, replace the
self-signed HTTPS certificate with a CA-signed one.

See :ref:`certificates` and :ref:`https_certificates`.

Step 7 — Bring up your first VPN
--------------------------------

* **Site-to-site tunnel** between two gateways or to a third-party peer:
  follow the end-to-end walkthrough in :ref:`site_to_site`.
* **Remote-access (dial-up) VPN** for laptops and phones: configure the
  gateway side in :ref:`remote_access_vpn`, then set up each client using
  :ref:`remote_access_clients`.

Verify
------

* **VPN -> Active Sessions** shows the tunnel/session as *ESTABLISHED* with
  child SAs installed.
* Traffic passes end-to-end (for example, ping a host across the tunnel).
* **Monitoring -> IPsec** counters increase while traffic flows
  (see :ref:`statistics`).

If something fails, see :ref:`troubleshooting`.
