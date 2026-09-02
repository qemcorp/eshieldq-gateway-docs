.. _common_operations:

Common Operations
=================

Step-by-step recipes for routine administrative tasks. Each recipe assumes you
are logged in as an administrator.

.. _op_replace_https_cert:

Replace the HTTPS certificate with a CA-signed certificate
----------------------------------------------------------

Browsers warn on the factory self-signed management certificate; replace it
with one signed by a CA your clients trust.

#. Create a CSR: **PKI & Secrets -> Keys & CSRs -> New Signing Request**.
   Include the management IP address and/or DNS name in the SAN fields —
   browsers validate the SAN, not the Common Name.
#. Download the CSR and sign it with your CA (see :ref:`cert_signing`),
   including the ``serverAuth`` EKU.
#. Upload the signed certificate from the Signing Request table
   (**Actions -> Upload Signed Certificate**) with **usage**
   ``HTTPS_SERVER``. The web server switches to the new certificate.
#. Distribute the CA root certificate to the browsers/clients that access the
   management interface.

REST API: POST ``/api/certs/v1/signing_request``, then
POST ``/api/certs/v1/signed_csr`` (``usage: HTTPS_SERVER``).

**Verify:** reload the Web UI — the browser shows the new certificate
(GET ``/api/certs/v1/tls/server-cert`` returns its details).

.. _op_rotate_ipsec_cert:

Rotate an IPsec certificate before it expires
---------------------------------------------

#. Check current validity dates on the **Certificates** page
   (**Actions -> View Details**) or with GET ``/api/certs/v1/details``.
#. Create a new CSR, sign it with your CA, and upload it with usage
   ``IPSEC`` — the same procedure as :ref:`site_to_site` Step 2. The old
   certificate remains until you remove it.
#. Edit each connection that uses the old certificate and select the new
   **Local Certificate**, then re-activate the connection.
#. Once no connection references it, delete the old certificate from the
   **Certificates** page.

**Verify:** connections re-establish on **VPN -> Active Sessions**;
GET ``/api/ipsec/v1/sas`` shows the SAs up.

.. _op_enforce_mfa:

Enforce MFA for all users
-------------------------

#. Have every **administrator** enroll OTP first
   (**My Account -> One-Time Password** — scan the QR code with an authenticator
   app, then confirm the code). Enforcement is **refused** while any active
   administrator has no factor: they would be left holding a session that can
   only reach enrollment, and the enrollment code is itself issued by an
   administrator. See :ref:`user_management`.
#. Enable **OTP enforcement** on **System -> Security**
   (or POST ``/api/auth/v1/settings`` with ``otp_enforce: true``).
#. Ordinary users do **not** have to enroll beforehand. With enforcement on, a
   user who has not enrolled still signs in, but the session reaches nothing
   except enrollment until they finish it.
#. By default that enrollment needs a single-use code from an administrator
   (**Users -> issue enrollment code**, or POST
   ``/api/users/v1/{username}/otp/activation-code``), so a stolen password
   alone cannot register an attacker's authenticator. Clear
   ``otp_enrollment_requires_admin_token`` only for a supervised rollout.

.. note::

   Turning enforcement on ends the sessions that predate it, so everyone signs
   in again under the new policy. Turning it on is also refused if it would
   leave the appliance with no enrolled administrator, and for the same reason
   you cannot delete, deactivate or de-enroll the last enrolled administrator
   while it is on.

**Verify:** log out and back in — the login now requires the one-time
password.

.. _op_operator_account:

Add a read-only (operator) account
----------------------------------

Give auditors and NOC staff monitoring access without change permissions.

#. **System -> Users & Access -> Add User**, role **operator**
   (or POST ``/api/users/v1/register`` with ``role: operator``).
#. The operator can view configuration and statistics but every write is
   rejected (HTTP 403) and configuration controls are disabled in the UI;
   operators have no access to user management, security settings, or audit
   logs. Details in :ref:`roles_and_permissions`.

**Verify:** log in as the operator — configuration buttons are disabled, and
the user-management pages are not accessible.

.. _op_software_update:

Install a software update safely
--------------------------------

Updates install to the inactive bank of the dual-bank root filesystem, so a
failed install does not affect the running system (see :ref:`updates`).

#. Record your configuration (connections, ACL rules, users) in case you need
   to rebuild — for example with the Python client or GET requests for each
   area.
#. Check for updates: **System -> Maintenance -> Check for Updates**
   (POST ``/api/sys/v1/swupdate-check``), then watch
   GET ``/api/sys/v1/swupdate-check-status`` until the image download
   completes.
#. Install: POST ``/api/sys/v1/swupdate-install`` (same status endpoint
   reports install progress).
#. Reboot to switch to the new version: POST ``/api/sys/v1/reboot``.
   Schedule this in a maintenance window — the dataplane restarts and tunnels
   re-establish.

**Verify:** GET ``/api/sys/v1/version`` shows the new version;
**System -> Status & Health** is healthy; tunnels re-established. On failure, check
GET ``/api/sys/v1/logs/swupdate`` — the system boots the previous bank if the
install did not complete.

.. _op_disconnect_user:

Disconnect a remote-access VPN user
-----------------------------------

#. Find the session on **VPN -> Active Sessions** (remote-access sessions
   show the authenticated user and assigned virtual IP).
#. Select **Actions -> Disconnect** on the row, or POST
   ``/api/ipsec/v1/sas/terminate-session/<unique_id>`` (the ``unique_id``
   comes from GET ``/api/ipsec/v1/sas``).
#. To prevent reconnection, also remove or disable the credential: delete the
   local VPN user (DELETE ``/api/ipsec/v1/users/<username>``) or disable the
   account on your RADIUS server.

**Verify:** the session disappears from **Active Sessions**; the audit log
records the termination.
