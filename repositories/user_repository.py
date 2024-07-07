from dataclasses import asdict
from models.user import User
from models.user import Label
from firebase_admin import firestore

class UserRepository:
    db_con = None
    collection_name = 'users'

    @staticmethod
    def create(data):
        user = User(**data)
        user_ref = UserRepository.db_con.db.collection(UserRepository.collection_name).add(asdict(user))
        label = UserRepository.get_last_label()
        UserRepository.add_label_for_user(user_ref[1].id, label)
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

    @staticmethod
    def add_label_for_user(user_id, label):
        label = Label(label=label, user_id=user_id)
        UserRepository.db_con.db.collection("labels").add(asdict(label))
        
    @staticmethod
    def generate_labels():
        # batch_size = 500
        # docs = UserRepository.db_con.db.collection("labels").limit(batch_size).stream()
        # deleted = 0

        # for doc in docs:
        #     print(f'Deleting doc {doc.id}')
        #     doc.reference.delete()
        #     deleted += 1

        # print(f'Deleted {deleted} labels')

        students = UserRepository.read_by_type('student')
        l = 0
        for student in students:
            label = Label(label=l, user_id=student['id'])
            UserRepository.db_con.db.collection("labels").add(asdict(label))
            l+=1
            
    @staticmethod
    def get_last_label():
        labels_ref = UserRepository.db_con.db.collection("labels").order_by('label', direction=firestore.Query.DESCENDING).limit(1)
        last_label = labels_ref.limit(1).get()
        last_label = next(iter(last_label), None)
        return last_label.to_dict().get('label', 0) + 1 if last_label else 0
        
    @staticmethod
    def get_user_id_by_label(label):
        label_ref = UserRepository.db_con.db.collection("labels").where('label', '==', label).stream()
        label = next(label_ref, None)
        return label.to_dict().get('user_id') if label else None
