import requests
from typing import Dict, List, Optional
from requests.exceptions import RequestException

import qonto_mcp
from qonto_mcp import mcp


@mcp.tool()
def create_client(
    kind: str,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    name: Optional[str] = None,
    email: Optional[str] = None,
    extra_emails: Optional[List[str]] = None,
    phone: Optional[Dict] = None,
    currency: Optional[str] = None,
    locale: Optional[str] = None,
    vat_number: Optional[str] = None,
    tax_identification_number: Optional[str] = None,
    e_invoicing_address: Optional[str] = None,
    recipient_code: Optional[str] = None,
    billing_address: Optional[Dict] = None,
    delivery_address: Optional[Dict] = None,
) -> Dict:
    """
    Create a client (customer) in Qonto. Qonto does not enforce uniqueness — call
    get_clients first to check whether a matching client already exists.

    Required-field combinations (validated server-side, not locally):
        - kind="individual" or kind="freelancer" → first_name AND last_name required
        - kind="company" → name required
    For invoicing, currency and locale are also required server-side.

    Args:
        kind: Client type. One of "individual", "freelancer", "company".
        first_name: Given name (max 60). Required for individual/freelancer.
        last_name: Family name (max 60). Required for individual/freelancer.
        name: Display name (max 250). Required for company; optional otherwise.
        email: Primary contact email.
        extra_emails: Additional contact emails (max 100 items).
        phone: {"country_code": "+33", "number": "123456789"}.
        currency: ISO 4217 alpha-3 code (e.g. "EUR"). Required for invoicing.
        locale: Language for documents. One of "FR", "EN", "IT", "DE", "ES".
                Required for invoicing.
        vat_number: VAT number (max 20). France format: "FR" + 2-char checksum + 9-digit SIREN.
        tax_identification_number: National tax id (max 20). E.g. SIREN/SIRET (FR),
                                    Codice Fiscale (IT), NIF/CIF (ES), Steuernummer (DE).
        e_invoicing_address: French e-invoicing address (SIREN format). France only.
        recipient_code: SDI recipient code. Italy only.
        billing_address: {"street_address": str (max 250), "city": str (max 50),
                          "zip_code": str (max 20; IT requires 5 chars),
                          "province_code": str (2 chars; required for IT),
                          "country_code": str (ISO 3166, 2 chars)}.
        delivery_address: Same structure as billing_address.

    Example:
        create_client(
            kind="company",
            name="Acme GmbH",
            email="billing@acme.de",
            currency="EUR",
            locale="DE",
            vat_number="DE123456789",
            billing_address={
                "street_address": "Hauptstraße 1",
                "city": "Berlin",
                "zip_code": "10115",
                "country_code": "DE",
            },
        )
    """
    url = f"{qonto_mcp.thirdparty_host}/v2/clients"

    body: Dict = {"kind": kind}

    optional_fields = {
        "first_name": first_name,
        "last_name": last_name,
        "name": name,
        "email": email,
        "extra_emails": extra_emails,
        "phone": phone,
        "currency": currency,
        "locale": locale,
        "vat_number": vat_number,
        "tax_identification_number": tax_identification_number,
        "e_invoicing_address": e_invoicing_address,
        "recipient_code": recipient_code,
        "billing_address": billing_address,
        "delivery_address": delivery_address,
    }
    for key, value in optional_fields.items():
        if value is not None:
            body[key] = value

    try:
        response = requests.post(url, headers=qonto_mcp.headers, json=body)
        response.raise_for_status()
        return response.json()
    except RequestException as e:
        raise RuntimeError(f"Failed to create client: {str(e)}")


@mcp.tool()
def update_client(
    client_id: str,
    kind: Optional[str] = None,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    name: Optional[str] = None,
    email: Optional[str] = None,
    extra_emails: Optional[List[str]] = None,
    phone: Optional[Dict] = None,
    currency: Optional[str] = None,
    locale: Optional[str] = None,
    vat_number: Optional[str] = None,
    tax_identification_number: Optional[str] = None,
    e_invoicing_address: Optional[str] = None,
    recipient_code: Optional[str] = None,
    billing_address: Optional[Dict] = None,
    delivery_address: Optional[Dict] = None,
) -> Dict:
    """
    Partially update an existing client. Only provided fields are changed.

    Args:
        client_id: UUID of the client to update.
        kind: Client type. One of "individual", "freelancer", "company". Changing to
              "individual" clears any vat_number on the client.
        first_name: Given name (max 60). Required by Qonto when kind="individual"/"freelancer".
        last_name: Family name (max 60). Required by Qonto when kind="individual"/"freelancer".
        name: Display name (max 250). Required by Qonto when kind="company".
        email: Primary contact email.
        extra_emails: Additional contact emails (max 100 items).
        phone: {"country_code": "+33", "number": "123456789"}.
        currency: ISO 4217 alpha-3 code (e.g. "EUR").
        locale: Document language. One of "FR", "EN", "IT", "DE", "ES".
        vat_number: VAT number (max 20).
        tax_identification_number: National tax id (max 20).
        e_invoicing_address: French e-invoicing address (SIREN format). France only.
        recipient_code: SDI recipient code. Italy only.
        billing_address: {"street_address": str, "city": str, "zip_code": str,
                          "province_code": str, "country_code": str (ISO 3166)}.
        delivery_address: Same structure as billing_address.

    Example:
        update_client(
            client_id="33v418bb-bd0d-4df4-865c-c07afab8bb48",
            email="new-billing@acme.de",
        )
    """
    url = f"{qonto_mcp.thirdparty_host}/v2/clients/{client_id}"

    body: Dict = {}
    optional_fields = {
        "kind": kind,
        "first_name": first_name,
        "last_name": last_name,
        "name": name,
        "email": email,
        "extra_emails": extra_emails,
        "phone": phone,
        "currency": currency,
        "locale": locale,
        "vat_number": vat_number,
        "tax_identification_number": tax_identification_number,
        "e_invoicing_address": e_invoicing_address,
        "recipient_code": recipient_code,
        "billing_address": billing_address,
        "delivery_address": delivery_address,
    }
    for key, value in optional_fields.items():
        if value is not None:
            body[key] = value

    try:
        response = requests.patch(url, headers=qonto_mcp.headers, json=body)
        response.raise_for_status()
        return response.json()
    except RequestException as e:
        raise RuntimeError(f"Failed to update client: {str(e)}")


@mcp.tool()
def get_clients(
    current_page: Optional[int] = None,
    per_page: Optional[int] = None,
) -> Dict:
    """
    Get all clients from Qonto API.

    Args:
        current_page: The current page of results to retrieve.
        per_page: The number of results per page.

    Example: get_clients(per_page=20)
    """
    url = f"{qonto_mcp.thirdparty_host}/v2/clients"
    params = {}
    if current_page is not None:
        params["current_page"] = current_page
    if per_page is not None:
        params["per_page"] = per_page

    try:
        response = requests.get(url, headers=qonto_mcp.headers, params=params)
        response.raise_for_status()
        return response.json()
    except RequestException as e:
        raise RuntimeError(f"Error fetching clients: {str(e)}")


@mcp.tool()
def get_client(client_id: str) -> Dict:
    """
    Get a specific client from Qonto API.

    Args:
        client_id: The ID of the client to retrieve.

    Example: get_client(client_id="a1b2c3d4-5678-90ab-cdef-ghijklmnopqr")
    """
    url = f"{qonto_mcp.thirdparty_host}/v2/clients/{client_id}"

    try:
        response = requests.get(url, headers=qonto_mcp.headers)
        response.raise_for_status()
        return response.json()
    except RequestException as e:
        raise RuntimeError(f"Error getting client: {str(e)}")
