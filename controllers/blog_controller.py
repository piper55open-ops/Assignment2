from models.blog_model import BlogModel

class BlogController:
    def __init__(self):
        self.model = BlogModel()
        self.model.create_table()

    def list_blogs(self):
        return self.model.get_all_blogs()

    def get_blog(self, blog_id):
        return self.model.get_blog_by_id(blog_id)

