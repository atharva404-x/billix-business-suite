
from fastapi import APIRouter
from app.api.v1 import business, customers, suppliers, units, categories, products, inventory, invoices, reports

api_router = APIRouter(prefix="/v1")
api_router.include_router(business.router, tags=["business"])
api_router.include_router(customers.router, tags=["customers"])
api_router.include_router(suppliers.router, tags=["suppliers"])
api_router.include_router(units.router, tags=["units"])
api_router.include_router(categories.router, tags=["categories"])
api_router.include_router(products.router, tags=["products"])
api_router.include_router(inventory.router, tags=["inventory"])
api_router.include_router(invoices.router, tags=["invoices"])
api_router.include_router(reports.router, tags=["reports"])

__all__ = ["api_router"]
