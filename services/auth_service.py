class AuthService:
    """
    AuthService class for handling authentication and authorization.

    Attributes:
        db (DatabaseConnector): Instance of the DatabaseConnector class.
    """
    def __init__(self, database_connector):
        """
        Initializes the AuthService class.

        Args:
            database_connector (DatabaseConnector): Instance of the DatabaseConnector class.
        """
        self.db = database_connector
        
    def login(self, jwt_token: str) -> str:
        """
        Verifies the JWT token and returns the decoded token.

        Args:
            jwt_token (str): JWT token to be verified.

        Returns:
            str: Decoded token if the verification is successful, None otherwise.
        """
        try:
            decoded_token = self.db.auth.verify_id_token(jwt_token)
            return decoded_token
        except Exception as e:
            print(e)
            return None

    def logout(self, jwt_token: str) -> bool:
        """
        Revokes the refresh tokens associated with the user identified by the JWT token.

        Args:
            jwt_token (str): JWT token identifying the user.

        Returns:
            bool: True if the refresh tokens are successfully revoked, False otherwise.
        """
        try:
            decoded_token = self.db.auth.verify_id_token(jwt_token)
            uuid = decoded_token['user_id']
            self.db.auth.revoke_refresh_tokens(uuid)
            return True
        except Exception as e:
            print(e)
            return False
