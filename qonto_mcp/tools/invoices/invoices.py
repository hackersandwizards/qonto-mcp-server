import requests
from datetime import datetime
from typing import Dict, List, Optional
from requests.exceptions import RequestException

import qonto_mcp
from qonto_mcp import mcp


@mcp.tool()
def create_client_invoice_draft(
    client_id: str,
    issue_date: str,
    due_date: str,
    currency: str,
    iban: str,
    items: List[Dict],
    number: Optional[str] = None,
    purchase_order: Optional[str] = None,
    terms_and_conditions: Optional[str] = None,
    header: Optional[str] = None,
    footer: Optional[str] = None,
    upload_id: Optional[str] = None,
    performance_start_date: Optional[str] = None,
    performance_end_date: Optional[str] = None,
    discount: Optional[Dict] = None,
    settings: Optional[Dict] = None,
    report_einvoicing: Optional[bool] = None,
    payment_reporting: Optional[Dict] = None,
    welfare_fund: Optional[Dict] = None,
    withholding_tax: Optional[Dict] = None,
    stamp_duty_amount: Optional[str] = None,
) -> Dict:
    """
    Create a client invoice in DRAFT status only. Status is hardcoded to "draft"
    and cannot be set to "unpaid" or finalized through this tool.

    Args:
        client_id: UUID of the client. Client must have a currency set.
        issue_date: Issue date in YYYY-MM-DD format.
        due_date: Due date in YYYY-MM-DD format. Must be >= issue_date.
        currency: ISO 4217 currency code (e.g. "EUR"). Must match the client's currency.
        iban: IBAN for the payment method (ISO 13616). Must belong to a Qonto account.
        items: List of invoice line items. Each item is a dict with required fields
               `title` (str, max 40), `quantity` (decimal str), `unit_price`
               ({"value": str, "currency": str}), `vat_rate` (decimal str, e.g. "0.2"),
               and optional `description` (max 1800), `unit` (max 20),
               `vat_exemption_reason` (Italy only, codes N1-N7 / S-series), `discount`.
        number: Custom invoice number (max 40). Required if auto-numbering is disabled.
        purchase_order: Purchase order reference (max 40).
        terms_and_conditions: Free-text terms (max 525).
        header: Custom header text on the invoice.
        footer: Custom footer text on the invoice.
        upload_id: UUID of a previously uploaded attachment to attach to the invoice.
        performance_start_date: Start of performance period (YYYY-MM-DD). Required if
                                performance_end_date is set. Not updateable after
                                creation; Qonto's PATCH schema only accepts the
                                singular `performance_date` field.
        performance_end_date: End of performance period (YYYY-MM-DD). Must be
                              >= performance_start_date.
        discount: Top-level invoice discount, e.g. {"type": "percentage", "value": "0.1"}
                  or {"type": "absolute", "value": {"value": "10.00", "currency": "EUR"}}.
        settings: InvoiceSettingsOverride object overriding organization-level invoice
                  settings for this invoice.
        report_einvoicing: Italy only. Whether to report the invoice via SDI. Defaults to true.
        payment_reporting: Italy only. {"conditions": str, "method": str (enum code)}.
        welfare_fund: Italy only. {"type": str, "rate": str}.
        withholding_tax: Italy/Spain only. {"reason": str, "rate": str, "payment_reason": str}.
        stamp_duty_amount: Italy only. Decimal string, e.g. "1.00".

    Example:
        create_client_invoice_draft(
            client_id="33v418bb-bd0d-4df4-865c-c07afab8bb48",
            issue_date="2026-05-09",
            due_date="2026-06-09",
            currency="EUR",
            iban="FR1420041010050500013M02606",
            items=[{
                "title": "Consulting",
                "quantity": "10",
                "unit": "hour",
                "unit_price": {"value": "100.00", "currency": "EUR"},
                "vat_rate": "0.19",
            }],
            number="DRF-2026-001",
        )
    """
    url = f"{qonto_mcp.thirdparty_host}/v2/client_invoices"

    body: Dict = {
        "client_id": client_id,
        "issue_date": issue_date,
        "due_date": due_date,
        "currency": currency,
        "payment_methods": {"iban": iban},
        "items": items,
        "status": "draft",
    }

    optional_fields = {
        "number": number,
        "purchase_order": purchase_order,
        "terms_and_conditions": terms_and_conditions,
        "header": header,
        "footer": footer,
        "upload_id": upload_id,
        "performance_start_date": performance_start_date,
        "performance_end_date": performance_end_date,
        "discount": discount,
        "settings": settings,
        "report_einvoicing": report_einvoicing,
        "payment_reporting": payment_reporting,
        "welfare_fund": welfare_fund,
        "withholding_tax": withholding_tax,
        "stamp_duty_amount": stamp_duty_amount,
    }
    for key, value in optional_fields.items():
        if value is not None:
            body[key] = value

    try:
        response = requests.post(url, headers=qonto_mcp.headers, json=body)
        response.raise_for_status()
        return response.json()
    except RequestException as e:
        raise RuntimeError(f"Failed to create client invoice draft: {str(e)}")


@mcp.tool()
def update_client_invoice_draft(
    invoice_id: str,
    client_id: Optional[str] = None,
    issue_date: Optional[str] = None,
    due_date: Optional[str] = None,
    iban: Optional[str] = None,
    items: Optional[List[Dict]] = None,
    number: Optional[str] = None,
    purchase_order: Optional[str] = None,
    terms_and_conditions: Optional[str] = None,
    header: Optional[str] = None,
    footer: Optional[str] = None,
    upload_id: Optional[str] = None,
    performance_date: Optional[str] = None,
    discount: Optional[Dict] = None,
    settings: Optional[Dict] = None,
    report_einvoicing: Optional[bool] = None,
    payment_reporting: Optional[Dict] = None,
    welfare_fund: Optional[Dict] = None,
    withholding_tax: Optional[Dict] = None,
    stamp_duty_amount: Optional[str] = None,
) -> Dict:
    """
    Partially update a DRAFT client invoice. Only provided fields are changed.
    Server-side enforced: only invoices with status="draft" can be updated.
    Currency is not updateable (inherited from the client).

    Args:
        invoice_id: UUID of the draft invoice to update.
        client_id: New client UUID for the invoice.
        issue_date: New issue date (YYYY-MM-DD).
        due_date: New due date (YYYY-MM-DD). Must be >= issue_date.
        iban: Replacement IBAN for the payment method (ISO 13616). Must belong to a
              Qonto account. Wraps to {"payment_methods": {"iban": ...}}.
        items: Replacement list of invoice line items. Same item shape as in
               create_client_invoice_draft.
        number: Custom invoice number (max 40). Must be unique within organization.
        purchase_order: Purchase order reference (max 40).
        terms_and_conditions: Free-text terms (max 525).
        header: Custom header text.
        footer: Custom footer text.
        upload_id: UUID of an uploaded attachment to attach.
        performance_date: Single performance date (YYYY-MM-DD). Qonto's PATCH
                          schema only accepts this singular field, not the
                          performance_start_date / performance_end_date pair
                          available on create. Behavior on a draft that was
                          created with a performance period is undocumented —
                          verify before relying on it for periodic invoices.
        discount: Top-level invoice discount object.
        settings: InvoiceSettingsOverride object.
        report_einvoicing: Italy only. Whether to report via SDI.
        payment_reporting: Italy only.
        welfare_fund: Italy only.
        withholding_tax: Italy/Spain only.
        stamp_duty_amount: Italy only. Decimal string (max 15 chars).

    Example:
        update_client_invoice_draft(
            invoice_id="4d5418bb-bd0d-4df4-865c-c07afab8bb48",
            due_date="2026-07-01",
            number="DRF-2026-002",
        )
    """
    url = f"{qonto_mcp.thirdparty_host}/v2/client_invoices/{invoice_id}"

    body: Dict = {}
    if iban is not None:
        body["payment_methods"] = {"iban": iban}

    optional_fields = {
        "client_id": client_id,
        "issue_date": issue_date,
        "due_date": due_date,
        "items": items,
        "number": number,
        "purchase_order": purchase_order,
        "terms_and_conditions": terms_and_conditions,
        "header": header,
        "footer": footer,
        "upload_id": upload_id,
        "performance_date": performance_date,
        "discount": discount,
        "settings": settings,
        "report_einvoicing": report_einvoicing,
        "payment_reporting": payment_reporting,
        "welfare_fund": welfare_fund,
        "withholding_tax": withholding_tax,
        "stamp_duty_amount": stamp_duty_amount,
    }
    for key, value in optional_fields.items():
        if value is not None:
            body[key] = value

    try:
        response = requests.patch(url, headers=qonto_mcp.headers, json=body)
        response.raise_for_status()
        return response.json()
    except RequestException as e:
        raise RuntimeError(f"Failed to update client invoice draft: {str(e)}")


@mcp.tool()
def get_client_invoices(
    current_page: Optional[int] = None,
    per_page: Optional[int] = None,
    status: Optional[str] = None,
    updated_at_from: Optional[datetime] = None,
    updated_at_to: Optional[datetime] = None,
) -> Dict:
    """
    Get client invoices from Qonto API.

    Args:
        current_page: The current page of results to retrieve.
        per_page: The number of results per page.
        status: Filter invoices by status.
        updated_at_from: Filter invoices updated from this date.
        updated_at_to: Filter invoices updated until this date.

    Example: get_client_invoices(per_page=10, status="paid")
    """
    url = f"{qonto_mcp.thirdparty_host}/v2/client_invoices"
    params = {}
    if current_page is not None:
        params["current_page"] = current_page
    if per_page is not None:
        params["per_page"] = per_page
    if status is not None:
        params["status"] = status
    if updated_at_from is not None:
        params["updated_at_from"] = updated_at_from.isoformat()
    if updated_at_to is not None:
        params["updated_at_to"] = updated_at_to.isoformat()

    try:
        response = requests.get(url, headers=qonto_mcp.headers, params=params)
        response.raise_for_status()
        return response.json()
    except RequestException as e:
        raise RuntimeError(f"Failed to fetch client invoices {str(e)}")


@mcp.tool()
def get_supplier_invoices(
    current_page: Optional[int] = None,
    per_page: Optional[int] = None,
    status: Optional[str] = None,
    updated_at_from: Optional[datetime] = None,
    updated_at_to: Optional[datetime] = None,
) -> Dict:
    """
    Get supplier invoices from Qonto API.

    Args:
        current_page: The current page of results to retrieve.
        per_page: The number of results per page.
        status: Filter invoices by status.
        updated_at_from: Filter invoices updated from this date.
        updated_at_to: Filter invoices updated until this date.

    Example: get_supplier_invoices(per_page=10, status="pending")
    """
    url = f"{qonto_mcp.thirdparty_host}/v2/supplier_invoices"
    params = {}
    if current_page is not None:
        params["current_page"] = current_page
    if per_page is not None:
        params["per_page"] = per_page
    if status is not None:
        params["status"] = status
    if updated_at_from is not None:
        params["updated_at_from"] = updated_at_from.isoformat()
    if updated_at_to is not None:
        params["updated_at_to"] = updated_at_to.isoformat()

    try:
        response = requests.get(url, headers=qonto_mcp.headers, params=params)
        response.raise_for_status()
        return response.json()
    except RequestException as e:
        raise RuntimeError(f"Failed to fetch supplier invoices {str(e)}")


@mcp.tool()
def get_credit_notes(
    current_page: Optional[int] = None,
    per_page: Optional[int] = None,
    updated_at_from: Optional[datetime] = None,
    updated_at_to: Optional[datetime] = None,
) -> Dict:
    """
    Get credit notes from Qonto API.

    Args:
        current_page: The current page of results to retrieve.
        per_page: The number of results per page.
        updated_at_from: Filter credit notes updated from this date.
        updated_at_to: Filter credit notes updated until this date.

    Example: get_credit_notes(per_page=5)
    """
    url = f"{qonto_mcp.thirdparty_host}/v2/credit_notes"
    params = {}
    if current_page is not None:
        params["current_page"] = current_page
    if per_page is not None:
        params["per_page"] = per_page
    if updated_at_from is not None:
        params["updated_at_from"] = updated_at_from.isoformat()
    if updated_at_to is not None:
        params["updated_at_to"] = updated_at_to.isoformat()

    try:
        response = requests.get(url, headers=qonto_mcp.headers, params=params)
        response.raise_for_status()
        return response.json()
    except RequestException as e:
        raise RuntimeError(f"Failed to fetch credit notes {str(e)}")
