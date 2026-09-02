.. _faq:

Frequently Asked Questions
==========================

Deployment and networking
--------------------------

**Which ports must be open in my cloud firewall (NSG / security group)?**

* Management interface: TCP 443 (HTTPS) and TCP 22 (SSH).
* WAN interface: UDP 500 (IKE), UDP 4500 (IKE/NAT-T), and IP protocol 50
  (ESP).

**Why does no traffic pass even though everything looks configured?**

The dataplane ACL default is **deny-all** on both LAN and WAN. Add permit
rules before expecting any forwarded or tunneled traffic
(see :ref:`setup_acl_rules`). The management interface is not affected by the
dataplane ACLs.

**Is IPv6 supported?**

Dataplane addressing is IPv4 today; IPv6 support is planned
(see :ref:`network_setup`).

**How do I size the VM?**

Use at least 8 vCPUs with accelerated/ENA networking for high-bandwidth
workloads; throughput scales with vCPU count. Compute-optimized instance
types give the best results (see your cloud chapter). Note that Confidential
VM types reduce performance (see :ref:`confidential_vm`).

VPN
---

**Can I use a pre-shared key (PSK) instead of certificates?**

No. IKE peer authentication is certificate/EAP-based only — PSK
authentication is deliberately not supported for security reasons.
(Postquantum Preshared Keys — PPK, RFC 8784 — are different: they
*supplement* certificate authentication, see :ref:`post_quantum_safe_mlkem`.)
IKEv1 can be selected per connection for legacy interoperability, but IKEv2
is recommended and is required for EAP/remote-access authentication and
post-quantum key exchange.

**Which algorithms will the gateway negotiate?**

The **defaults** are CNSA-strength — AES-256-GCM, SHA-384, ECP-384 — and a
broader set can be selected per connection for interoperability: AES-128/192/
256 (CBC and GCM), SHA-256/384/512, DH groups MODP-2048/3072/4096,
ECP-256/384/521 and Curve25519, plus optional ML-KEM-768/1024 post-quantum
key exchange. The gateway only negotiates what the connection is configured
with, so a peer offering algorithms outside the connection's proposals still
fails with "no matching proposal" — the most common interop failure with
unconfigured Windows clients (see :ref:`client_windows`). An optional
CNSA-only enforcement mode restricts configuration to CNSA v1.0 algorithms
(ECP-384+, MODP-3072+, SHA-384+).

**Can road-warrior laptops and phones connect without extra client
software?**

Yes — the native Windows, macOS, and iOS IKEv2 clients, strongSwan, and
FortiClient are all supported. Per-client setup guides are in
:ref:`remote_access_clients`.

**Do I need a RADIUS server for remote-access users?**

No. EAP-MSCHAPv2 against the on-gateway local user database works without any
external server (see :ref:`remote_access_local_users`). RADIUS adds central
credential management, MFA challenges, and accounting.

**How many remote-access clients can connect?**

Each client leases a virtual IP from the connection's address pool, so the
pool size is the practical limit — size the pool (e.g. a ``/24`` for ~250
clients) to your user population (see :ref:`remote_access_pools`).

Management and security
-----------------------

**I lost my administrator password — how do I recover?**

There is no password-recovery backdoor. If another administrator account
exists, it can be used to reset your credentials. Keeping at least two
administrator accounts is recommended; the system always requires at least
one (the last administrator cannot be deleted).

**Why is my API session rejected after 30 minutes?**

Session tokens expire after the configured token timeout (default 30
minutes). Log in again, or adjust ``token_timeout_sec`` in the security
policy (see :ref:`security_policy`).

**Why can't I retrieve a password / RADIUS secret / PPK I configured?**

All secrets are **write-only** by design: they are stored encrypted and never
returned by any API or UI view. To change one, write a new value.

**Is there a configuration backup / restore?**

There is no single-click backup today. All configuration is readable through
the REST API (connections, pools, ACL rules, users, settings), so it can be
recorded and re-applied with scripts or the ``eshieldq-gateway-client`` Python library —
recommended before software updates (see :ref:`op_software_update`).

**What is the difference between the admin and operator roles?**

Administrators have full read/write access. Operators are read-only for
monitoring: they can view configuration and statistics but cannot change
anything, and have no access to user management, security settings, or audit
logs (see :ref:`roles_and_permissions`).

**Why do some features report "not licensed"?**

Features are gated by the device's signed license entitlements. Check
**System -> License** in the Web UI or GET ``/api/identity/v1/status``; a
missing/expired license disables the affected features until enrollment is
re-run (see :ref:`device_license`).

Updates
-------

**What happens if a software update fails or power is lost mid-install?**

Updates install to the inactive bank of a dual-bank root filesystem. If the
install does not complete, the system boots the previous version and the
update can simply be retried (see :ref:`updates`).
