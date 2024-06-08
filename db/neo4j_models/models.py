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
        print(addr_node)
        if not addr_node:
            return None
        transactions = await addr_node.transactions.all()
        return transactions

class Transaction(AsyncStructuredNode):
    transaction_hash = StringProperty(unique_index=True)
    value = FloatProperty()
    block_id = IntegerProperty()
    time = StringProperty()

    inputs = AsyncRelationshipFrom('Address', 'INPUT')
    outputs = AsyncRelationshipTo('Address', 'OUTPUT')


async def main():
    # res = await Transaction.nodes
    # print(res)
    res = await Address.find_transactions('bc1q7cyrfmck2ffu2ud3rn5l5a8yv6f0chkp0zpemf')
    print(res)

if __name__ == "__main__":
    asyncio.run(main())
