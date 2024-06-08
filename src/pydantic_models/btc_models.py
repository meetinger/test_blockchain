from pydantic import BaseModel, Field, ConfigDict


class TransactionModel(BaseModel):
    transaction_hash: str = Field(..., example="923c1db0664683b5cdcd5b5c656b0a8ae7bbd8f6638ce2f34ac59924ce65efc6")
    value: float = Field(..., example=0.0)
    block_id: int = Field(..., example=0)
    time: str = Field(..., example="2022-01-01T00:00:00+00:00")


class InputsOutputsTransactionsModel(BaseModel):
    inputs: list[TransactionModel] = Field(..., example=[])
    outputs: list[TransactionModel] = Field(..., example=[])

class AddressModel(BaseModel):
    address: str = Field(..., example="bc1qf43tdrym26qlz8rg06f88wg35n27uhcf29zs4f")
    balance: float = Field(..., example=0.0)

    transactions: InputsOutputsTransactionsModel = Field(..., example={'inputs': [], 'outputs': []})