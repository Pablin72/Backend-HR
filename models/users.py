class User:
    def __init__(self, _id, type_id, name, lastname, email, phone_number, birth):
        self._id = _id
        self.type_id = type_id        
        self.name = name
        self.lastname = lastname
        self.email = email
        self.phone_number = phone_number
        self.birth = birth

    @classmethod
    def from_dict(cls, user_dict):
        return cls(
            user_dict['_id'],
            user_dict['type_id'],            
            user_dict['name'],
            user_dict['lastname'],
            user_dict['email'],
            user_dict['phone_number'],
            user_dict['birth']
        )

class UserManager:
    def __init__(self, mongo_client, db_name, collection_name):
        self.db = mongo_client[db_name]
        self.collection = self.db[collection_name]

    def create_user(self, user_data):
        # Asegúrate de que no estás pasando un _id aquí
        _id = self.collection.insert_one(user_data).inserted_id
        return _id            


    def get_user(self, _id):
        user_data = self.collection.find_one({'_id': _id})
        return User.from_dict(user_data) if user_data else None

    def edit_user(self, _id, updated_data):
        result = self.collection.update_one({'_id': _id}, {'$set': updated_data})
        return result.modified_count > 0

    def delete_user(self, _id):
        result = self.collection.delete_one({'_id': _id})
        return result.deleted_count > 0