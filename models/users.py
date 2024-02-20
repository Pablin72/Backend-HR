class User:
    def __init__(self, gov_id, name, lastname, email, phone_number, birth):
        self.gov_id = gov_id
        self.name = name
        self.lastname = lastname
        self.email = email
        self.phone_number = phone_number
        self.birth = birth

    @classmethod
    def from_dict(cls, user_dict):
        return cls(
            user_dict['gov_id'],
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
        user_id = self.collection.insert_one(user_data).inserted_id
        return user_id            


    def get_user(self, user_id):
        user_data = self.collection.find_one({'_id': user_id})
        return User.from_dict(user_data) if user_data else None

    def edit_user(self, user_id, updated_data):
        result = self.collection.update_one({'_id': user_id}, {'$set': updated_data})
        return result.modified_count > 0

    def delete_user(self, user_id):
        result = self.collection.delete_one({'_id': user_id})
        return result.deleted_count > 0