import asyncio

from neomodel import (StringProperty, IntegerProperty, FloatProperty, AsyncStructuredNode, AsyncRelationshipFrom, AsyncRelationshipTo)
from neomodel import config as neo_config

from core.settings import settings
from src.pydantic_models.btc_models import TransactionModel, AddressModel
neo_config.DATABASE_URL = settings.neo4j_url


class Address(AsyncStructuredNode):
    address = StringProperty(unique_index=True)
    transactions = AsyncRelationshipFrom('Transaction', 'TRANSACTION_RELATION')

    @property
    async def balance(self):
        transactions = await self.transactions.all()
        balance = 0.0
        for transaction in transactions:
            inputs = await transaction.inputs.all()
            outputs = await transaction.outputs.all()

            for input_addr in inputs:
                if input_addr.address == self.address:
                    balance -= transaction.value

            for output_addr in outputs:
                if output_addr.address == self.address:
                    balance += transaction.value

        return balance

    async def to_pydantic(self):
        address_model = AddressModel(
            address=self.address,
            balance=await self.balance,
            transactions=[await t.to_pydantic() for t in await self.transactions.all()]
        )

        return address_model

    def __str__(self):
        return f"Address(address={self.address})"


class Transaction(AsyncStructuredNode):
    transaction_hash = StringProperty(unique_index=True)
    value = FloatProperty()
    block_id = IntegerProperty()
    time = StringProperty()

    inputs = AsyncRelationshipFrom('Address', 'TRANSACTION_RELATION')
    outputs = AsyncRelationshipTo('Address', 'TRANSACTION_RELATION')

    def __str__(self):
        return (f"Transaction(transaction_hash={self.transaction_hash}, "
                f"value={self.value}, block_id={self.block_id}, "
                f"time={self.time})")

    async def to_pydantic(self):
        return TransactionModel(
            transaction_hash=self.transaction_hash,
            value=self.value,
            block_id=self.block_id,
            inputs=[i.address for i in await self.inputs.all()],
            outputs=[o.address for o in await self.outputs.all()],
            time=self.time
        )
