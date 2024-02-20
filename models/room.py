from datetime import datetime
from itertools import combinations
from pymongo import MongoClient

def is_room_available(room, start_date, end_date):
    # Si no hay fechas de ocupación, la habitación está disponible
    if not room.occupancy:
        return True

    start_date = datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.strptime(end_date, '%Y-%m-%d')
    
    for occupancy_period in room.occupancy:
        occupied_start = datetime.strptime(occupancy_period['checkin'], '%Y-%m-%d')
        occupied_end = datetime.strptime(occupancy_period['checkout'], '%Y-%m-%d')
        if start_date < occupied_end and end_date > occupied_start:
            return False
    return True
def prefilter_rooms(rooms, start_date, end_date):
    return [room for room in rooms if is_room_available(room, start_date, end_date)]

class Room:
    def __init__(self, _id, description, occupancy, people_capacity, price, qty_beds, room_type, size, images):
        self._id = _id
        self.description = description
        self.occupancy = occupancy
        self.people_capacity = people_capacity
        self.price = price
        self.qty_beds = qty_beds
        self.room_type = room_type
        self.size = size
        self.images = images

    @classmethod
    def from_dict(cls, room_dict):
        return cls(
            room_dict['_id'],
            room_dict['description'],
            room_dict.get('occupancy', []),
            room_dict['people_capacity'],
            room_dict['price'],
            room_dict['qty_beds'],
            room_dict['room_type'],
            room_dict['size'],
            room_dict.get('images', [])
        )

class RoomManager:
    def __init__(self, mongo_client, db_name, collection_name):
        self.db = mongo_client[db_name]
        self.collection = self.db[collection_name]

    

    def find_room_combinations(self, num_people, start_date, end_date, num_rooms):
        rooms = self.get_rooms()
        available_rooms = prefilter_rooms(rooms, start_date, end_date)
        
        valid_combinations = []

        for r in range(num_rooms, num_rooms + 1):  # Solo buscamos combinaciones con el número exacto de habitaciones
            for combo in combinations(available_rooms, r):
                total_capacity = sum(room.people_capacity for room in combo)
                if total_capacity >= num_people:  
                    valid_combinations.append({
                        "rooms": combo,
                        "total_capacity": total_capacity,
                        "excess_capacity": total_capacity - num_people
                    })

        # Ordena las combinaciones válidas primero por menor exceso de capacidad y luego por menor número de habitaciones
        valid_combinations.sort(key=lambda x: (x['excess_capacity'], len(x['rooms'])))
        
        return valid_combinations[:10] if len(valid_combinations) >= 10 else valid_combinations


    def get_rooms(self):
        rooms_data = self.collection.find()
        rooms = [Room.from_dict(h) for h in rooms_data]
        return rooms
    
if __name__ == "__main__":
    mongo_client = MongoClient('mongodb://localhost:27017/')
    room_manager = RoomManager(mongo_client=mongo_client, db_name="hotel", collection_name="rooms")

    start_date_str = "2024-01-15"
    end_date_str = "2024-01-20"

    room_combinations = room_manager.find_room_combinations(num_people=3, start_date=start_date_str, end_date=end_date_str, num_rooms=3)
    
    # Imprimir los resultados
    for combo in room_combinations:
    # Accede a la lista de habitaciones en 'combo' con la clave 'rooms'
        rooms_in_combo = combo['rooms']
        print("Rooms in this combination:")
        for room in rooms_in_combo:
            print(room.__dict__)  # Imprime el diccionario de atributos de cada objeto Room
        print("Total capacity of this combination:", combo['total_capacity'])
        print("Excess capacity of this combination:", combo['excess_capacity'])
        print("----")


    