from fastapi import APIRouter

transactions_router = APIRouter(prefix="/transactions", tags=["transactions"])


@transactions_router.get("/{transaction_hash}")
async def get_transaction(transaction_hash: str):
    return