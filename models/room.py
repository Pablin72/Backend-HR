from datetime import datetime
from itertools import combinations
from pymongo import MongoClient
from dotenv import load_dotenv
load_dotenv
import os
mongo_uri = os.getenv('MONGO_URI')


# Conectar a la base de datos MongoDB
mongo_client = MongoClient(mongo_uri)

def is_room_available(room, start_date, end_date):
    # Si no hay fechas de ocupación, la habitación está disponible
    if not room.occupancy:
        return True

    start_date = datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.strptime(end_date, '%Y-%m-%d')
    
    for occupancy_period in room.occupancy:
        occupied_start = datetime.strptime(occupancy_period[0], '%Y-%m-%d')
        occupied_end = datetime.strptime(occupancy_period[1], '%Y-%m-%d')
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
    
    def to_dict(self):
        return {
            "_id": self._id,
            "description": self.description,
            "occupancy": self.occupancy,
            "people_capacity": self.people_capacity,
            "price": self.price,
            "qty_beds": self.qty_beds,
            "room_type": self.room_type,
            "size": self.size,
            "images": self.images
        }

class RoomManager:
    def __init__(self, mongo_client, db_name, collection_name):
        self.db = mongo_client[db_name]
        self.collection = self.db[collection_name]

    def get_room_by_id(self, room_id):
        room_data = self.collection.find_one({"_id": int(room_id)})
        return Room.from_dict(room_data) if room_data else None

    

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
    
    def update_room(self, room_id, occupancy_period):
        # Obtener la habitación por su ID
        room = self.get_room_by_id(room_id)
        if not room:
            return False  # Habitación no encontrada

        # Agregar el periodo de ocupación al array 'occupancy'
        room.occupancy.append([occupancy_period['checkin_date'], occupancy_period['checkout_date']])

        # Actualizar la habitación en la base de datos
        result = self.collection.update_one(
            {"_id": int(room_id)},
            {"$set": {"occupancy": room.occupancy}}
        )

        return result.modified_count > 0  # Devolver True si se modificó al menos un documento


    def get_rooms(self):
        rooms_data = self.collection.find()
        rooms = [Room.from_dict(h) for h in rooms_data]
        return rooms
    
    def deleteOccupancy(self, checkin, checkout, new_checkin, new_checkout, ids):
        print("Entro a deleteOccupancy")
        for i in ids:
            room = self.get_room_by_id(i)
            if room:
                for j in range(len(room.occupancy)):
                    print("Cuarto: ", i)
                    print("Checkin: ", room.occupancy[j][0])
                    print("Checkout: ", room.occupancy[j][1])
                    print("Checkin front: ", checkin)
                    print("Checkout front: ", checkout)
                    if room.occupancy[j][0] == checkin and room.occupancy[j][1] == checkout:
                        print("Entro a if")
                        room.occupancy[j] = [new_checkin, new_checkout] # Eliminar el período de ocupación
                        print(room.occupancy[j])
                        break
                # Actualizar la habitación en la base de datos
                result = self.collection.update_one(
                    {"_id": int(i)},
                    {"$set": {"occupancy": room.occupancy}}
                )
                if result.modified_count == 0:
                    return False  # No se pudo actualizar la habitación
            else:
                return False  # Habitación no encontrada
        return True  # Todas las ocupaciones eliminadas correctamente

    
if __name__ == "__main__":
    mongo_client = MongoClient(mongo_uri)
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


    