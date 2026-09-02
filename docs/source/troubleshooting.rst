.. _troubleshooting:

Troubleshooting
===============

Where to look first
-------------------

Almost every problem leaves evidence in a log stream or a statistics counter:

* **Logs** — Web UI **Monitoring -> Logs**, or
  GET ``/api/sys/v1/logs/<log_name>`` with ``<log_name>`` one of ``audit``,
  ``ipsec``, ``ssh``, ``http-access``, ``rest-api``, ``swupdate``,
  ``user-auth``, ``crypto``, ``eaas``.
* **Statistics** — Web UI **Statistics** page, or ``/api/stats/v1/*`` and
  ``/api/stats/v2/errors`` (see :ref:`statistics`).
* **System state** — **System -> Status & Health**, or
  GET ``/api/sys/v1/status`` and GET ``/api/sys/v1/system-report``.

.. _troubleshooting_https:

Cannot reach the Web UI / REST API
----------------------------------

Log to check: ``http-access``; also ``rest-api``.

.. list-table::
   :header-rows: 1
   :widths: 30 35 35

   * - Symptom
     - Likely cause
     - Fix
   * - Connection times out
     - Cloud network rules do not allow TCP 443 to the MGMT interface, or you
       are using the wrong (WAN/LAN) address
     - Allow HTTPS in the NSG / security group; connect to the **management**
       IP address
   * - Browser certificate warning
     - Factory self-signed HTTPS certificate
     - Add a one-time browser exception, then install a CA-signed certificate
       (see :ref:`op_replace_https_cert`)
   * - HTTP ``400`` before login is even attempted
     - Mutual TLS is enabled and the client presented no certificate
     - Present the client certificate, or disable Mutual TLS from the CLI
       (see :ref:`tls_config`)

.. _troubleshooting_login:

Cannot log in
-------------

Logs to check: ``user-auth`` and ``audit``.

.. list-table::
   :header-rows: 1
   :widths: 30 35 35

   * - Symptom
     - Likely cause
     - Fix
   * - ``401`` with correct password
     - MFA (OTP) is enabled or enforced and no/stale one-time password was
       supplied
     - Provide the current OTP (REST: ``client_secret`` field of
       ``/api/auth/v2/token``); confirm the device clock generating the OTP is
       correct — TOTP is time-based
   * - Authenticator lost; user cannot log in
     - The seed is shown only at enrollment and is never readable again
     - An administrator resets the user's password
       (``PATCH /api/users/v1/{username}``), which clears the factor, then the
       user enrolls a new one. Nothing can recover the old seed.
   * - ``401`` from ``/api/auth/v1/otp/enroll`` with the right password
     - OTP is enforced and this session is enrollment-scoped, so a single-use
       administrator code is required
     - Get one from **Users -> issue enrollment code** (REST:
       ``POST /api/users/v1/{username}/otp/activation-code``). Codes are
       single-use and expire.
   * - ``409`` when enabling OTP enforcement
     - An active administrator has no second factor enrolled; the response
       names them
     - Have each named administrator enroll, then enable enforcement
   * - New user cannot be created
     - Password does not meet the 14-character minimum / complexity rules
     - Choose a compliant password
   * - Session drops after ~30 minutes
     - Token timeout in the security policy
     - Log in again, or raise ``token_timeout_sec`` (see
       :ref:`security_policy`); it accepts 60 to 86400 seconds
   * - Password suddenly rejected
     - Password expired (``password_timeout_sec``, default 90 days)
     - Change the password, or adjust the policy
   * - ``429 Too Many Requests`` with a ``Retry-After``, even with the correct
       password
     - Too many failed logins from this client address for this account: the
       login lockout is refusing attempts without checking the credential
       (see :ref:`security_policy`)
     - Wait out the ``Retry-After`` interval (default 300 s) — continued
       attempts do not extend it. To get in immediately, log in from a
       different client address: a lockout applies to one address/account pair.
       Check the ``user-auth`` log for the failures that caused it before
       raising the threshold
   * - Console CLI reports ``Could not verify the gateway's TLS certificate``
       and stops without re-prompting
     - The appliance's HTTPS certificate no longer matches the copy the CLI
       pins at ``/var/nginx/server_certs/ss_server_cert.crt``. Normally a
       certificate regenerated after a hostname change, or an interrupted
       rotation. The CLI refuses rather than continuing unverified
     - Complete the certificate change: set the hostname and its certificate
       from the Web UI or REST API (see :ref:`certificates`), then start the
       CLI again. If the appliance is otherwise unreachable, use the serial
       console. Never work around this by disabling verification — the same
       message appears when a peer is impersonating the appliance

.. _troubleshooting_ssh:

SSH access
----------

Log to check: ``ssh``.

.. list-table::
   :header-rows: 1
   :widths: 30 35 35

   * - Symptom
     - Likely cause
     - Fix
   * - Permission denied (publickey)
     - The SSH user/public key was not registered
     - Add the user and key (see :ref:`ssh_user_mgmt`); connect with
       ``ssh -i <keyfile> <ssh_user>@<mgmt_address>``
   * - Key accepted but the CLI asks for a login
     - Expected behaviour — SSH authenticates the transport; the CLI requires
       a username + password (+ OTP) login
     - Log in with CLI/REST credentials (see :ref:`user_management`)
   * - Connection times out
     - TCP 22 not allowed to the MGMT interface
     - Fix the cloud network rules

.. _troubleshooting_ipsec_issues:

Site-to-site tunnel will not establish
--------------------------------------

Log to check: ``ipsec`` (the IKE daemon log — the single most useful place
for VPN problems). See also the walkthrough in :ref:`site_to_site`.

.. list-table::
   :header-rows: 1
   :widths: 30 35 35

   * - Symptom
     - Likely cause
     - Fix
   * - No response from the peer / retransmits
     - UDP 500/4500 or ESP blocked — cloud rules or WAN dataplane ACLs on
       either side; or wrong peer address
     - Allow IKE/ESP in both the cloud rules and the gateway ACLs
       (see :ref:`setup_acl_rules`); verify the WAN public IPs
   * - Authentication failed
     - Peer certificate does not chain to the uploaded CA, or the configured
       Remote ID does not match the peer certificate's subject/SAN
     - Upload the correct CA; make the IDs match the certificates
   * - No matching proposal
     - The peer offers algorithms that are not in the connection's configured
       proposals (defaults: AES-256-GCM / SHA-384 / ECP-384)
     - Align the peer with the connection's proposals, or add a matching
       proposal (e.g. AES-128-GCM, SHA-256, ECP-256) to the connection
   * - Activation fails
     - A stale instance of the connection is still loaded
     - Deactivate/terminate the connection, then re-activate
   * - PPK mismatch
     - Peers configured with different PPK ID or data
     - Set the identical PPK ID and value on both peers
       (see :ref:`post_quantum_safe_mlkem`)

.. _troubleshooting_no_traffic:

Tunnel is up but traffic does not flow
--------------------------------------

**Check the ACLs first** — the dataplane default is deny-all, and an
established tunnel says nothing about whether the ACLs permit the tunneled
traffic. ACL deny-drops are counted in **Monitoring -> System Counters (Errors)**
(``/api/stats/v2/errors``) and **Firewall -> Sessions & Drops**.

.. list-table::
   :header-rows: 1
   :widths: 30 35 35

   * - Symptom
     - Likely cause
     - Fix
   * - Nothing passes in either direction
     - LAN/WAN ACLs deny the traffic
     - Add permit rules for the tunneled networks (see
       :ref:`example_acl_rules`)
   * - One direction works
     - Traffic selectors do not mirror each other, or the far side's return
       route/ACL is missing
     - Make ``local_ts``/``remote_ts`` mirror images; check routes and ACLs on
       the peer
   * - Hosts behind the LAN cannot be reached
     - Cloud routing does not direct the subnet through the gateway's LAN
       interface
     - Fix the cloud route table (see your cloud chapter, e.g.
       :ref:`azure_overview`)
   * - Drops under load
     - Traffic exceeds system capacity — crypto or NIC ``missed`` counters
       rising
     - Check ``/api/stats/v1/crypto`` and ``/api/stats/v1/hw``; use a larger
       VM size or reduce offered load

.. _troubleshooting_remote_access:

Remote-access (dial-up) clients
-------------------------------

Log to check: ``ipsec`` (includes EAP and RADIUS forwarding); ``audit`` for
authentication events. Client-side guides: :ref:`remote_access_clients`.

.. list-table::
   :header-rows: 1
   :widths: 30 35 35

   * - Symptom
     - Likely cause
     - Fix
   * - Client rejects the gateway certificate / "policy mismatch"
     - Gateway certificate SAN does not contain the address the client dialed,
       ``serverAuth`` EKU missing, or the CA is not installed on the device
     - Re-issue the gateway certificate with correct SAN/EKU; install the CA
       root on the client
   * - IKE fails immediately from Windows
     - Windows offered its weak default algorithms
     - Apply the PowerShell IPsec policy from :ref:`client_windows`
   * - EAP authentication fails (local users)
     - Wrong username/password, or the connection's Remote Authentication is
       not *EAP-MSCHAPv2 (local users)*
     - Verify the user exists (GET ``/api/ipsec/v1/users``) and the
       connection's ``remote_auth_method``
   * - EAP authentication fails (RADIUS)
     - RADIUS server unreachable, wrong shared secret, or the server does not
       accept EAP-MSCHAPv2
     - Verify server address/ports/secret on **VPN -> Remote Access (RADIUS)**; confirm the
       RADIUS server logs show the request; check the failover order
   * - Connects but gets no virtual IP
     - No address pool attached to the connection, or the pool is exhausted
     - Attach/grow the pool (see :ref:`remote_access_pools`)
   * - Static IP not honoured
     - RADIUS ``Framed-IP-Address`` requires the connection's pool set to the
       ``radius`` sentinel; a local user's static IP must lie inside the pool
       range
     - See :ref:`remote_access_static_ip`
   * - Connected but no traffic
     - Dataplane ACLs, or the client's traffic selectors do not cover the
       destination
     - See :ref:`troubleshooting_no_traffic`

.. _troubleshooting_directory_auth:

Directory authentication (LDAP / AD)
------------------------------------

Log to check: ``radius`` — the authentication broker's own log, and the place
directory failures are explained in words. ``GET /api/sys/v1/logs/radius``, or
**Monitor -> Logs** in the Web UI. Setup guide: :ref:`directory_auth`.

Work from the top of this table down: **Test connectivity** isolates
infrastructure problems from user problems, so run it before reading anything
else.

.. list-table::
   :header-rows: 1
   :widths: 30 35 35

   * - Symptom
     - Likely cause
     - Fix
   * - "Can't contact LDAP server"
     - The gateway cannot reach the directory, or cannot resolve its name
     - Confirm routing to the directory from the gateway's own subnet, and that
       DNS is configured (:ref:`dns_config`). On a cloud deployment check the
       security group / NSG allows 636 from the gateway
   * - TLS handshake fails / certificate not trusted
     - Wrong CA pasted, an incomplete chain, or the server certificate was
       issued to a different name than the one configured
     - Re-export the **CA** certificate (not the server's own), and use the
       exact DNS name the certificate was issued to
   * - Configuration refused: "server ... is an IP address"
     - A bare IP was entered as a directory server
     - Use the DNS name. A certificate cannot vouch for an IP address, so an IP
       is refused at configuration time rather than failing later in a handshake
   * - Service bind fails, users cannot be found
     - Wrong Bind DN, wrong password, or a Base DN that does not contain the
       users
     - Run **Test connectivity**. Check the Bind DN is a full DN. Re-enter the
       password — a blank field keeps the stored one, it does not clear it
   * - A user authenticates in the directory but the VPN refuses them
     - They are not in an allowed group, or nested membership is not resolved
     - Run **Test user**: it reports authorization separately from
       authentication. On Active Directory enable **Nested Groups** —
       ``memberOf`` lists only direct membership
   * - Everyone is refused right after a working setup
     - The service account's password expired or the account was locked
     - Check the account in the directory; re-enter the password on the gateway
   * - The directory settings are saved but no one uses them
     - An external RADIUS server still owns EAP authentication
     - The two are mutually exclusive. Remove the RADIUS configuration
       (:ref:`remote_access_radius`)
   * - Windows clients fail; strongSwan clients work
     - The broker is presenting its self-signed fallback certificate, which
       tunnelled EAP (EAP-TTLS) clients reject
     - Set an EAP server certificate the clients trust; see
       :ref:`directory_auth_eap_certificate`
   * - Accounts lock out in the directory
     - The gateway's lockout threshold is at or above the directory's own
     - Set the gateway threshold **below** the directory policy so the gateway
       stops the attempts first
   * - The probe returns 429
     - The credential probe is rate limited to 10 per minute per administrator
     - Wait for the window to pass. It is a diagnostic, not a bulk checker

.. _troubleshooting_swupdate:

Software update
---------------

Log to check: ``swupdate``.

.. list-table::
   :header-rows: 1
   :widths: 30 35 35

   * - Symptom
     - Likely cause
     - Fix
   * - Download fails
     - No internet reachability from the management network, or a transient
       CDN error
     - Verify DNS/outbound HTTPS; retry POST ``/api/sys/v1/swupdate-check``
   * - Install fails
     - Transient failure writing the inactive bank
     - Retry the install; if it persists, reboot and retry — the dual-bank
       design keeps the running system safe (see :ref:`updates`)
   * - Version unchanged after install
     - The reboot step was skipped
     - POST ``/api/sys/v1/reboot``, then GET ``/api/sys/v1/version``

.. _troubleshooting_system_errors:

System health
-------------

If GET ``/api/sys/v1/status`` or the **System -> Status & Health** page reports failed
components:

* Components come up at different times after boot; the system is normally
  ready within ~30 seconds, but allow more time before concluding a component
  has failed.
* A reboot (POST ``/api/sys/v1/reboot``) recovers most transient failures.
* GET ``/api/sys/v1/system-report`` summarises security settings and open
  ports — useful evidence when reporting an issue.
* Security-relevant events (IMA, SELinux, Lockdown violations) appear in the
  ``audit`` log (see :ref:`audit_log`).

Reporting issues
----------------

When reporting an issue include the software version
(GET ``/api/sys/v1/version``), the system report
(GET ``/api/sys/v1/system-report``), and the relevant log excerpts.
