import asyncio

from neomodel import StringProperty, IntegerProperty, RelationshipTo, RelationshipFrom, FloatProperty, \
    StructuredRel, AsyncStructuredNode, adb
from neomodel import config as neo_config

from core.settings import settings

neo_config.DATABASE_URL = settings.neo4j_url

class Address(AsyncStructuredNode):
    address = StringProperty(unique_index=True)

    inputs = RelationshipFrom('Transaction', 'INPUT')
    outputs = RelationshipTo('Transaction', 'OUTPUT')


class Transaction(AsyncStructuredNode):
    transaction_hash = StringProperty()
    value = FloatProperty()
    block_id = IntegerProperty()
    time = IntegerProperty()

    @classmethod
    async def find_transactions(cls, address):
        query = """
        MATCH (a:Address {address: $address})-[:INPUT]->(tx:Transaction)<-[:OUTPUT]-(b:Address)
        RETURN tx
        UNION
        MATCH (a:Address {address: $address})<-[:OUTPUT]-(tx:Transaction)-[:INPUT]->(b:Address)
        RETURN tx
        """
        results, meta = await adb.cypher_query(query, {'address': address})
        return [Transaction.inflate(row[0]) for row in results]


class Inputs(AsyncStructuredNode):
    value = FloatProperty()
    time = IntegerProperty()
    recipient = StringProperty()


class Outputs(AsyncStructuredNode):
    value = FloatProperty()
    time = IntegerProperty()
    recipient = StringProperty()

async def main():
    res = await Transaction.find_transactions('bc1q052rew5ade79c62fzh9wuxh03lfrh65dg2a5kr')
    print(res)

if __name__ == "__main__":
    asyncio.run(main())
