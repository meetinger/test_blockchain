import asyncio

from neomodel import StringProperty, IntegerProperty, RelationshipTo, RelationshipFrom, FloatProperty, \
    StructuredRel, AsyncStructuredNode, adb, AsyncRelationshipFrom, AsyncRelationshipTo
from neomodel import config as neo_config

from core.settings import settings

neo_config.DATABASE_URL = settings.neo4j_url

class Address(AsyncStructuredNode):
    address = StringProperty(unique_index=True)

    transactions = AsyncRelationshipFrom('Transaction', 'TO_ADDRESS')


class Transaction(AsyncStructuredNode):
    transaction_hash = StringProperty(unique_index=True)
    value = FloatProperty()
    block_id = IntegerProperty()
    time = StringProperty()

    inputs = AsyncRelationshipFrom('Address', 'TO_TRANSACTION')
    outputs = AsyncRelationshipTo('Address', 'TO_TRANSACTION')

    @classmethod
    async def find_transactions(cls, address: str):
        addr_node = await Address.nodes.get_or_none(address=address)
        if not addr_node:
            return None

        transactions = await addr_node.transactions.all()
        return transactions


async def main():
    res = await Transaction.find_transactions('bc1qyqjx4m2sweyj3lh6jxx4e5z2xczkarq8lglpj8')
    print(res)

if __name__ == "__main__":
    asyncio.run(main())
