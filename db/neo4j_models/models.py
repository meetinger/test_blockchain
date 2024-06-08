import asyncio

from neomodel import StringProperty, IntegerProperty, RelationshipTo, RelationshipFrom, FloatProperty, \
    StructuredRel, AsyncStructuredNode, adb, AsyncRelationshipFrom, AsyncRelationshipTo
from neomodel import config as neo_config

from core.settings import settings

neo_config.DATABASE_URL = settings.neo4j_url


class Address(AsyncStructuredNode):
    address = StringProperty(unique_index=True)
    transactions = AsyncRelationshipFrom('Transaction', 'TO_ADDRESS')

    @classmethod
    async def find_transactions(cls, address: str):
        addr_node = await cls.nodes.get_or_none(address=address)
        if addr_node is None:
            return None
        return await addr_node.transactions.all()


class Transaction(AsyncStructuredNode):
    transaction_hash = StringProperty(unique_index=True)
    value = FloatProperty()
    block_id = IntegerProperty()
    time = StringProperty()

    inputs = AsyncRelationshipTo('Address', 'TO_ADDRESS')
    outputs = AsyncRelationshipTo('Address', 'TO_ADDRESS')



async def main():
    # res = await Transaction.nodes
    # print(res)
    res = await Address.find_transactions('bc1qf43tdrym26qlz8rg06f88wg35n27uhcf29zs4f')
    print(res)

if __name__ == "__main__":
    asyncio.run(main())
