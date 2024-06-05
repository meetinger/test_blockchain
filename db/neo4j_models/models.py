from neomodel import StructuredNode, StringProperty, IntegerProperty, RelationshipTo, RelationshipFrom


class Transaction(StructuredNode):
    transaction_id = StringProperty(unique_index=True, required=True)
    block_id = StringProperty()
    timestamp = IntegerProperty()
    sent_by = RelationshipFrom('Address', 'SENT')
    received_by = RelationshipTo('Address', 'RECEIVED')


class Address(StructuredNode):
    address = StringProperty(unique_index=True, required=True)
    balance = IntegerProperty(default=0)
    sent = RelationshipTo(Transaction, 'SENT')
    received = RelationshipFrom(Transaction, 'RECEIVED')
