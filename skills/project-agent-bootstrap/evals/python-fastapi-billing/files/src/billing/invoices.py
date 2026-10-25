from fastapi import APIRouter

router = APIRouter(prefix="/invoices")


@router.post("")
def create_invoice(customer_id: str, amount_cents: int):
    ...


@router.post("/{invoice_id}/send")
def send_invoice(invoice_id: int):
    ...
