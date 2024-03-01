from datetime import datetime
from uuid import uuid4

class Refund:
    def __init__(self, reason, value, user_id, booking_id):
        self.reason = reason
        self.value = value
        self.user_id = user_id
        self.booking_id = booking_id

    @classmethod
    def from_dict(cls, refund_dict):
        return cls(
            refund_dict['reason'],
            refund_dict['value'],
            refund_dict['user_id'],
            refund_dict['booking_id']
        )

    def to_dict(self):
        return {
            "reason": self.reason,
            "value": self.value,
            "user_id": self.user_id,
            "booking_id": self.booking_id
        }


class RefundManager:
    def __init__(self, mongo_client, db_name, collection_name):
        self.db = mongo_client[db_name]
        self.collection = self.db[collection_name]

    def get_refunds(self):
        refunds_data = self.collection.find()
        refunds = [Refund.from_dict(r) for r in refunds_data]
        return refunds

    def get_refund_by_id(self, _id):
        try:
            refund_data = self.collection.find_one({"_id": _id})
            return Refund.from_dict(refund_data) if refund_data else None
        except ValueError:
            return None

    def write_refund(self, refund):
        refund_dict = refund.to_dict()
        result = self.collection.insert_one(refund_dict)
        return result.inserted_id

    def update_refund(self, _id, updated_refund):
        updated_data = updated_refund.to_dict()
        result = self.collection.update_one({"_id": _id}, {"$set": updated_data})
        return result.modified_count

    def delete_refund(self, _id):
        result = self.collection.delete_one({"_id": _id})
        return result.deleted_count
