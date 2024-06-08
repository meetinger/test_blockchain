from fastapi import APIRouter, HTTPException, status

from db.neo4j_models.models import Address
from src.pydantic_models.btc_models import AddressModel

addresses_router = APIRouter(prefix="/addresses")


@addresses_router.get("/{address}", response_model=AddressModel)
async def get_address(address: str):
    address_db = await Address.nodes.get_or_none(address=address)
    if address_db is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Address not found")

    address_data = {
        'address': address_db.address,
        'balance': await address_db.balance
    }

    return AddressModel.model_validate(address_data)

