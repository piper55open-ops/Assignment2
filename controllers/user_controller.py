from models.user_model import UserModel
from werkzeug.security import generate_password_hash, check_password_hash

class UserController:
    def __init__(self):
        self.model = UserModel()

    def register_user(self, username, email, password, role, image=None):
        hashed_password = generate_password_hash(password)
        self.model.add_user(username, email, hashed_password, role, image)

    def login_user(self, email, password):
        user = self.model.get_user_by_email(email)
        if user and check_password_hash(user["password"], password):
            return user
        return None
