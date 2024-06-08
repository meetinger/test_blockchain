from fastapi import APIRouter

from src.api.addresses.addresses import addresses_router
from src.api.system.system import system_router
from src.api.transactions.transactions import transactions_router

base_router = APIRouter()

base_router.include_router(addresses_router)
base_router.include_router(transactions_router)
base_router.include_router(system_router)