from dataclasses import asdict
from models.user import User

class UserRepository:
    db_con = None
    collection_name = 'users'

    @staticmethod
    def create(data):
        user = User(**data)
        user_ref = UserRepository.db_con.db.collection(UserRepository.collection_name).add(asdict(user))
        return {'id': user_ref[1].id, **asdict(user)}
        
    @staticmethod
    def update(user_id, data):
        user_ref = UserRepository.db_con.db.collection(UserRepository.collection_name).document(user_id)
        user_ref.update(data)
        return {'id': user_id, **user_ref.get().to_dict()}

    @staticmethod
    def delete(user_id):
        user_ref = UserRepository.db_con.db.collection(UserRepository.collection_name).document(user_id)
        user_ref.delete()

    @staticmethod
    def read(user_id):
        user_ref = UserRepository.db_con.db.collection(UserRepository.collection_name).document(user_id)
        user = user_ref.get()
        return {'id': user_id, **user.to_dict()} if user.exists else None        
    
    @staticmethod
    def read_all():
        users_ref = UserRepository.db_con.db.collection(UserRepository.collection_name).stream()
        return [{'id': user.id, **user.to_dict()} for user in users_ref]

    @staticmethod
    def read_by_email(email):
        users_ref = UserRepository.db_con.db.collection(UserRepository.collection_name).where('email', '==', email).stream()
        user = next(users_ref, None)
        return {'id': user.id, **user.to_dict()} if user else None

    @staticmethod
    def read_by_type(type):
        users_ref = UserRepository.db_con.db.collection(UserRepository.collection_name).where('type', '==', type).stream()
        return [{'id': user.id, **user.to_dict()} for user in users_ref]
