.. _release_notes:

Release Notes
=============

Release 3.1
-----------

Release 3.1 is the first release of the eShield-Q Gateway. It supports the
capabilities below; each links to the chapter that covers it.

Deployment
~~~~~~~~~~

* Virtual appliance for :ref:`Microsoft Azure <azure_overview>`,
  :ref:`Google Cloud <google_overview>` and :ref:`AWS <aws_overview>`, deployed
  with separate management, WAN and LAN network interfaces.
* :ref:`Confidential VM <confidential_vm>` and :ref:`vTPM <vtpm_support>`
  platforms. The device identity key is held on the appliance's encrypted
  ``/var`` volume and never leaves the instance.

Site-to-site VPN
~~~~~~~~~~~~~~~~

* Route-based point-to-point IPsec over IKEv2 with certificate authentication
  (see :ref:`site_to_site`). Pre-shared-key peer authentication is deliberately
  not supported.
* CNSA v1.0 algorithm defaults, per-connection selection of AES-128/192/256 in
  GCM and CBC, SHA-2, MODP/ECP/Curve25519 groups, and an optional CNSA-only
  enforcement mode (see :ref:`security`).
* Post-quantum key exchange: ML-KEM-768/1024 for IKEv2 (RFC 9370, RFC 9242) and
  post-quantum pre-shared keys (PPK, RFC 8784) — see
  :ref:`post_quantum_safe_mlkem`.
* AES-256-GCM data plane above 10 Gbps, scaling with the vCPU count of the VM
  (see :ref:`performance_features`).
* IKEv1 selectable per connection for legacy interoperability.

Remote-access (dial-up) VPN
~~~~~~~~~~~~~~~~~~~~~~~~~~~

* EAP-TLS, EAP-RADIUS and EAP-MSCHAPv2 client authentication
  (see :ref:`remote_access_auth_methods`).
* :ref:`LDAP / Active Directory <directory_auth>` authentication, and a
  :ref:`local VPN user database <remote_access_local_users>` that needs no
  external server.
* :ref:`RADIUS <remote_access_radius>` with an ordered server failover list.
* :ref:`Virtual-IP address pools <remote_access_pools>` with optional
  :ref:`static per-user addresses <remote_access_static_ip>`.
* :ref:`Client profile export <remote_access_client_profile>` and setup guides
  for the native Windows, macOS and iOS IKEv2 clients, strongSwan and
  FortiClient (see :ref:`remote_access_clients`).
* :ref:`Session monitoring and administrative disconnect
  <remote_access_sessions>`.

Firewall and networking
~~~~~~~~~~~~~~~~~~~~~~~

* Stateful and stateless ACL firewall with Layer 2-4 filtering, IP and MAC+IP
  rules and per-rule counters (see :ref:`acl_setup`). The default policy is
  **deny-all**, so permit rules are required before any traffic is forwarded.
* Interface addressing and :ref:`role assignment
  <interface_role_assignment>`, static :ref:`routes <route_setup>` and
  :ref:`FIB <fib_table>` inspection.
* :ref:`DNS with DNSSEC <dns_config>`, DHCP and NTP.

Certificates and secrets
~~~~~~~~~~~~~~~~~~~~~~~~

* :ref:`Certificate import <cert_import>`, :ref:`signing requests <cert_csr>`,
  :ref:`certificate details <cert_details>` and :ref:`revocation lists
  <cert_revocation_lists>`.
* Separate certificate usages for the IPsec identity and the
  :ref:`management HTTPS server certificate <https_certificates>`.
* Enforced certificate key strengths: RSA 3072-bit and above, ECC P-384 and
  above.
* On-device :ref:`private key <private_keys>` generation, and
  :ref:`Entropy as a Service <entropy_service>` for authorised clients.
* Every secret — passwords, RADIUS shared secrets and PPKs — is write-only:
  stored encrypted and never returned by the API or the Web UI.

Management
~~~~~~~~~~

* :ref:`Web user interface <api_docs>`, an OpenAPI 3.0
  :ref:`REST API <rest_api>` over HTTPS (TLS 1.2+), and a
  :ref:`CLI <cli_docs>` over SSH and the serial console.
* :ref:`Python client SDK <python_client>` for the REST API.
* :ref:`Role-based access control <roles_and_permissions>` with administrator
  and read-only operator roles.
* :ref:`Multi-factor authentication <op_enforce_mfa>` (OTP) with optional
  system-wide enforcement and administrator-issued enrollment codes.
* :ref:`Client certificate authentication (mutual TLS) <tls_config>` for the
  management interface.
* :ref:`Security policy <security_policy>` controls for session and password
  timeouts and for login lockout after repeated failed attempts.
* :ref:`SSH user management <ssh_user_mgmt>` with certificate-based
  authentication.

Monitoring and logging
~~~~~~~~~~~~~~~~~~~~~~

* :ref:`System status and health <system_monitoring>`, machine identity,
  software version, and a security-oriented :ref:`system report
  <system_report>`.
* :ref:`Interface <stats_interfaces>`, :ref:`IPsec <stats_ipsec>`,
  :ref:`hardware <stats_hardware>`, :ref:`crypto <stats_crypto>`,
  :ref:`dataplane runtime <stats_runtime>` and :ref:`error <stats_errors>`
  counters, with live charts and time-series history.
* Per-stream :ref:`log retrieval <system_logs>` and an
  :ref:`audit log <audit_log>` of security-relevant events, including integrity
  measurement, SELinux and kernel lockdown violations.
* :ref:`Syslog <syslog_configuration>`, with optional authenticated and
  encrypted transport over TLS.

Device identity, licensing and updates
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* Per-device cryptographic :ref:`identity <device_identity>` and automatic
  :ref:`enrollment <device_enrollment>` using the cloud platform's attested
  identity document — no operator secret is entered on the device.
* A signed :ref:`license <device_license_status>` listing the device's
  entitlements, and periodic :ref:`device key health and update-readiness
  <device_key_health>` reporting.
* Administrator-triggered :ref:`re-enrollment <device_reenrollment>`, so an
  appliance picks up an entitlement added to the subscription after it was
  deployed. Each instance stays bound to a single device key; re-registering an
  appliance whose key has changed is a supported, audited support operation
  (see :ref:`device_key_changed`).
* Authenticated and encrypted in-place :ref:`software update <updates>` to a
  dual-bank root filesystem, with automatic rollback if an install does not
  complete.
