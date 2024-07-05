import firebase_admin
from firebase_admin import credentials, auth, db, firestore


class DatabaseConnector:

    def __init__(self, credentials_path: str):
        self.credentials = credentials.Certificate(credentials_path)
        self.auth_app = firebase_admin.initialize_app(self.credentials)

        self.db = firestore.client()
        self.auth = auth
