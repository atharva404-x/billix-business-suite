
import uuid
from datetime import datetime
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.auth.permissions import Permission, PermissionChecker
from app.core.database import get_db_session
from app.models.user import User
from app.schemas.reports import CustomerReportsResponse, DashboardResponse, InventoryReportsResponse, PaymentReportsResponse, ProductReportsResponse, SalesReportResponse
from app.services.reports import ReportingService

router = APIRouter(prefix="/reports", tags=["reports"])

@router.get("/dashboard", response_model=DashboardResponse)
async def get_dashboard(
    business_id: uuid.UUID,
    current_user: Annotated[User, Depends(PermissionChecker(Permission.REPORT_READ))],
    session: AsyncSession = Depends(get_db_session)
):
    service = ReportingService(session)
    return await service.get_dashboard(current_user.id, business_id)

@router.get("/sales", response_model=SalesReportResponse)
async def get_sales_report(
    business_id: uuid.UUID,
    current_user: Annotated[User, Depends(PermissionChecker(Permission.REPORT_READ))],
    session: AsyncSession = Depends(get_db_session),
    group_by: str = Query("day", pattern="day|week|month|year"),
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None
):
    service = ReportingService(session)
    return await service.get_sales_report(
        current_user.id, business_id, group_by, date_from, date_to
    )

@router.get("/customers", response_model=CustomerReportsResponse)
async def get_customer_reports(
    business_id: uuid.UUID,
    current_user: Annotated[User, Depends(PermissionChecker(Permission.REPORT_READ))],
    session: AsyncSession = Depends(get_db_session),
    report_type: Optional[str] = Query(None, pattern="top|highest_spending|outstanding|purchase_history|revenue"),
    customer_id: Optional[uuid.UUID] = None
):
    service = ReportingService(session)
    return await service.get_customer_reports(
        current_user.id, business_id, report_type, customer_id
    )

@router.get("/products", response_model=ProductReportsResponse)
async def get_product_reports(
    business_id: uuid.UUID,
    current_user: Annotated[User, Depends(PermissionChecker(Permission.REPORT_READ))],
    session: AsyncSession = Depends(get_db_session),
    report_type: Optional[str] = Query(None, pattern="top_selling|least_selling|inactive|stock_value|current_stock|stock_movement")
):
    service = ReportingService(session)
    return await service.get_product_reports(
        current_user.id, business_id, report_type
    )

@router.get("/payments", response_model=PaymentReportsResponse)
async def get_payment_reports(
    business_id: uuid.UUID,
    current_user: Annotated[User, Depends(PermissionChecker(Permission.REPORT_READ))],
    session: AsyncSession = Depends(get_db_session),
    report_type: Optional[str] = Query(None, pattern="received|pending|overdue|distribution|outstanding")
):
    service = ReportingService(session)
    return await service.get_payment_reports(
        current_user.id, business_id, report_type
    )

@router.get("/inventory", response_model=InventoryReportsResponse)
async def get_inventory_reports(
    business_id: uuid.UUID,
    current_user: Annotated[User, Depends(PermissionChecker(Permission.REPORT_READ))],
    session: AsyncSession = Depends(get_db_session),
    report_type: Optional[str] = Query(None, pattern="valuation|low_stock|out_of_stock|stock_movement")
):
    service = ReportingService(session)
    return await service.get_inventory_reports(
        current_user.id, business_id, report_type
    )
