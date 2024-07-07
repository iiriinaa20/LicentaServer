class AuthService:

    def __init__(self, database_connector):
        self.db = database_connector
        
    def login(self, jwt_token: str) -> str:
        try:
            decoded_token = self.db.auth.verify_id_token(jwt_token)
            return decoded_token
        except Exception as e:
            print(e)
            return None

    def logout(self, jwt_token: str) -> bool:
        try:
            decoded_token = self.db.auth.verify_id_token(jwt_token)
            uuid = decoded_token['user_id']
            self.db.auth.revoke_refresh_tokens(uuid)
            return True
        except Exception as e:
            print(e)
            return False
