
from fastapi import APIRouter
from app.api.v1 import business, customers

api_router = APIRouter(prefix="/v1")
api_router.include_router(business.router, tags=["business"])
api_router.include_router(customers.router, tags=["customers"])

__all__ = ["api_router"]
