from fastapi import APIRouter, HTTPException, status

from db.neo4j_models.models import Transaction
from src.pydantic_models.btc_models import TransactionModel

transactions_router = APIRouter(prefix="/transactions", tags=["transactions"])


@transactions_router.get("/{transaction_hash}", response_model=TransactionModel)
async def get_transaction(transaction_hash: str):
    """Получить транзакцию по хэшу"""
    transaction_db = await Transaction.nodes.get_or_none(transaction_hash=transaction_hash)
    if transaction_db is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")

    return await transaction_db.to_pydantic()
