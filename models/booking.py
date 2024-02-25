from datetime import datetime

class Booking:
    def __init__(self, _id, user_id, checkin_date, checkout_date, qty_guests, rooms, total_price):
        self._id = _id
        self.user_id = user_id
        self.checkin_date = datetime.strptime(checkin_date, "%Y-%m-%d")
        self.checkout_date = datetime.strptime(checkout_date, "%Y-%m-%d")
        self.qty_guests = qty_guests
        self.rooms = rooms
        self.total_price = total_price

    @classmethod
    def from_dict(cls, booking_dict):
        return cls(
            booking_dict['_id'],
            booking_dict['user_id'],
            booking_dict['checkin_date'],
            booking_dict['checkout_date'],
            booking_dict['qty_guests'],
            booking_dict['rooms'],
            booking_dict['total_price']
        )

    def to_dict(self):
        return {
            "_id": self._id,
            "user_id": self.user_id,
            "checkin_date": self.checkin_date.strftime("%Y-%m-%d"),
            "checkout_date": self.checkout_date.strftime("%Y-%m-%d"),
            "qty_guests": self.qty_guests,
            "rooms": self.rooms,
            "total_price": self.total_price
        }

class BookingManager:
    def __init__(self, mongo_client, db_name, collection_name):
        self.db = mongo_client[db_name]
        self.collection = self.db[collection_name]

    def get_bookings(self):
        bookings_data = self.collection.find()
        bookings = [Booking.from_dict(b) for b in bookings_data]
        return bookings

    def get_booking_by_id(self, _id):
        try:
            booking_data = self.collection.find_one({"_id": int(_id)})
            return Booking.from_dict(booking_data) if booking_data else None
        except ValueError:
            return None

    def write_booking(self, booking):
        booking_dict = booking.to_dict()
        result = self.collection.insert_one(booking_dict)
        return result.inserted_id

    def update_booking(self, _id, updated_booking):
        updated_data = updated_booking.to_dict()
        # Convertir _id a entero
        _id = int(_id)
        result = self.collection.update_one({"_id": _id}, {"$set": updated_data})
        return result.modified_count



    def delete_booking(self, _id):
        result = self.collection.delete_one({"_id": int(_id)})
        return result.deleted_count
