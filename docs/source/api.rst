.. _rest_api:

Using the REST API
==================

Every management operation on the eShield-Q Gateway is available through an
OpenAPI 3.0 compliant HTTPS REST API — the Web UI is built on the same API.
This chapter shows how to authenticate and call it from scripts.

Interactive API documentation
-----------------------------

The gateway serves its own interactive (Swagger) API documentation, generated
from the running software so it always matches the installed version:

.. code-block:: console

    https://<management_ip_address>/api/docs

Each endpoint's request/response schema, field descriptions, and required
role are documented there. The raw OpenAPI schema is available at
``https://<management_ip_address>/api/openapi.json``.

.. _api_authentication:

Authentication
--------------

Log in by POSTing form-encoded credentials to ``/api/auth/v2/token``. On
success the gateway sets an ``access_token`` **session cookie** — subsequent
requests must present that cookie. The token expires after the configured
token timeout (default 30 minutes; see :ref:`security_policy`).

.. code-block:: bash

    GW="https://<management_ip_address>"

    # Log in and store the session cookie.
    # --cacert: the CA that signed the management HTTPS certificate
    #           (use -k only against a lab gateway with the factory
    #            self-signed certificate)
    curl --cacert ca.pem -c cookies.txt \
        -X POST "$GW/api/auth/v2/token" \
        -d "username=admin" \
        -d "password=<password>"

    # If MFA is enabled for the user, add the current one-time password:
    #   -d "client_secret=<6-digit OTP>"

    # Call the API with the stored cookie
    curl --cacert ca.pem -b cookies.txt "$GW/api/sys/v1/status"

    # Log out (invalidates the user's tokens)
    curl --cacert ca.pem -b cookies.txt -X POST "$GW/api/auth/v2/logout"

If Mutual TLS is enabled (see :ref:`tls_config`), also present the client
certificate: ``--cert client_cert.pem --key client_key.pem``.

.. _api_conventions:

Conventions
-----------

* **Roles** — write operations require an ``admin`` session; ``operator``
  sessions can read but every write returns ``403 Forbidden``
  (see :ref:`roles_and_permissions`).
* **Status codes** — ``401`` means not logged in or the session expired
  (log in again); ``403`` means logged in without permission; ``422`` means
  the request body failed validation (the response details which field).
* **Write-only secrets** — passwords, RADIUS shared secrets, PPKs, and EaaS
  client secrets are never returned by any endpoint. GETs return only
  non-secret metadata (for example a *secret configured* flag); to change a
  secret, write a new value.
* **Versioned paths** — endpoints are grouped as ``/api/<area>/v<n>/...``
  (for example ``/api/ipsec/v1/connections``, ``/api/auth/v2/token``).

Python client (SDK)
-------------------

The ``eshieldq-gateway-client`` Python package wraps the full API, handling
login, cookies, MFA, and Mutual TLS. Once published, it is installed by
running:

.. code-block:: bash

   pip install eshieldq-gateway-client

Source and examples: Quantum eMotion (|TBD-LINK|).
See :ref:`example_acl_rules` for a worked example using the client.
