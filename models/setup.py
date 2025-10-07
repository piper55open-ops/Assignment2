# setup_tables.py
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from models.blog_model import BlogModel
# Import other models here if you have more tables
# from models.user_model import UserModel
# from models.comment_model import CommentModel

def create_all_tables():
    blog_model = BlogModel()
    blog_model.create_table()

    # Similarly for other models
    # user_model = UserModel()
    # user_model.create_table()
    
    print("All tables created successfully!")

if __name__ == "__main__":
    create_all_tables()
