import asyncio

from neomodel import (StringProperty, IntegerProperty, FloatProperty, AsyncStructuredNode, AsyncRelationshipFrom, AsyncRelationshipTo)
from neomodel import config as neo_config

from core.settings import settings

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

    async def to_orm(self):
        dct = {
            'address': self.address,
            'balance': await self.balance,
            'transactions': self.transactions
        }


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





async def main():
    # node = await Address.nodes.get_or_none(address='bc1qm34lsc65zpw79lxes69zkqmk6ee3ewf0j77s3h')
    # # print(res)
    # res = await Address.find_transactions('bc1qf43tdrym26qlz8rg06f88wg35n27uhcf29zs4f')
    #
    #
    # pprint([str(i) for i in await node.transactions])


    # print('balance:', await node.balance)

    tr = await Transaction.nodes.get_or_none(
        transaction_hash='923c1db0664683b5cdcd5b5c656b0a8ae7bbd8f6638ce2f34ac59924ce65efc6'
    )
    print('inputs:', await tr.inputs.all())
    print('outputs:', await tr.outputs.all())

if __name__ == "__main__":
    asyncio.run(main())
