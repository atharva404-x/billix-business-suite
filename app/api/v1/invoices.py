
import uuid
from typing import Annotated, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db_session
from app.auth.dependencies import get_current_user
from app.models.user import User
from app.schemas.invoice import (
    InvoiceCreate,
    InvoiceUpdate,
    InvoiceResponse,
    InvoiceListResponse,
    PaymentCreate,
    PaymentResponse,
    PaymentListResponse
)
from app.models.invoice import InvoiceStatus, PaymentStatus
from app.services.invoice import InvoiceService
from app.repositories.invoice import PaymentRepository


router = APIRouter(prefix="/invoices", tags=["invoices"])


@router.post("", response_model=InvoiceResponse, status_code=201)
async def create_invoice(
    business_id: uuid.UUID,
    invoice_data: InvoiceCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    session: AsyncSession = Depends(get_db_session)
):
    service = InvoiceService(session)
    return await service.create_invoice(current_user.id, business_id, invoice_data)


@router.get("", response_model=InvoiceListResponse)
async def list_invoices(
    business_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    session: AsyncSession = Depends(get_db_session),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    status: Optional[InvoiceStatus] = Query(None),
    payment_status: Optional[PaymentStatus] = Query(None),
    search_query: Optional[str] = Query(None),
    customer_id: Optional[uuid.UUID] = Query(None),
    invoice_date_from: Optional[datetime] = Query(None),
    invoice_date_to: Optional[datetime] = Query(None),
    min_amount: Optional[float] = Query(None, ge=0),
    max_amount: Optional[float] = Query(None),
    sort_by: Optional[str] = Query(None),
    sort_order: str = Query("desc")
):
    service = InvoiceService(session)
    invoices, total = await service.list_invoices(
        current_user.id, business_id, skip, limit, status, payment_status, search_query,
        customer_id, invoice_date_from, invoice_date_to, min_amount, max_amount, sort_by, sort_order
    )
    return InvoiceListResponse(items=invoices, total=total)


@router.get("/{invoice_id}", response_model=InvoiceResponse)
async def get_invoice(
    business_id: uuid.UUID,
    invoice_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    session: AsyncSession = Depends(get_db_session)
):
    service = InvoiceService(session)
    return await service.get_invoice(current_user.id, business_id, invoice_id)


@router.patch("/{invoice_id}", response_model=InvoiceResponse)
async def update_invoice(
    business_id: uuid.UUID,
    invoice_id: uuid.UUID,
    update_data: InvoiceUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    session: AsyncSession = Depends(get_db_session)
):
    service = InvoiceService(session)
    return await service.update_invoice(current_user.id, business_id, invoice_id, update_data)


@router.post("/{invoice_id}/cancel", response_model=InvoiceResponse)
async def cancel_invoice(
    business_id: uuid.UUID,
    invoice_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    session: AsyncSession = Depends(get_db_session)
):
    service = InvoiceService(session)
    return await service.cancel_invoice(current_user.id, business_id, invoice_id)


@router.post("/payments", response_model=PaymentResponse, status_code=201)
async def record_payment(
    business_id: uuid.UUID,
    payment_data: PaymentCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    session: AsyncSession = Depends(get_db_session)
):
    service = InvoiceService(session)
    return await service.record_payment(current_user.id, business_id, payment_data)


@router.get("/{invoice_id}/payments", response_model=PaymentListResponse)
async def list_invoice_payments(
    business_id: uuid.UUID,
    invoice_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    session: AsyncSession = Depends(get_db_session),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100)
):
    service = InvoiceService(session)
    await service._ensure_business_access(current_user.id, business_id)
    repo = PaymentRepository(session)
    payments, total = await repo.list_by_invoice(business_id, invoice_id, skip, limit)
    return PaymentListResponse(items=payments, total=total)
