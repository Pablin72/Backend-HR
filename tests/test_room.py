import unittest
from unittest.mock import patch
from models.room import RoomManager

# Mock database calls
@patch('HR_backend.routes.room.room.MongoClient')
def test_find_room_combinations(self, mock_mongo_client):
    mock_collection = mock_mongo_client.return_value.hotel.rooms
    mock_collection.find.return_value = [
        {
            "_id": "5f4321098765432109876543",
            "description": "Habitación con cama doble",
            "occupancy": [],
            "people_capacity": 2,
            "price": 100,
            "qty_beds": 1,
            "room_type": "standard",
            "size": 20,
            "images": []
        },
        {
            "_id": "5f4321098765432109876544",
            "description": "Habitación con cama individual",
            "occupancy": [],
            "people_capacity": 1,
            "price": 50,
            "qty_beds": 1,
            "room_type": "standard",
            "size": 10,
            "images": []
        }
    ]

    room_manager = RoomManager(mongo_client=mock_mongo_client, db_name="hotel", collection_name="rooms")
    num_people = 3
    start_date = "2024-01-15"
    end_date = "2024-01-20"
    num_rooms = 3

    combinations = room_manager.find_room_combinations(num_people, start_date, end_date, num_rooms)

    # Assert expected properties of the returned combinations
    self.assertEqual(len(combinations), 1)  # Assuming one expected combination
    self.assertEqual(combinations[0]['total_capacity'], 3)
    self.assertEqual(combinations[0]['rooms'][0]['_id'], "5f4321098765432109876543")
    self.assertEqual(combinations[0]['rooms'][1]['_id'], "5f4321098765432109876544")

