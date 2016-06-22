from base import BaseHandler 

class MainHandler(BaseHandler):
    def get(self):
        self.render("blogHome.html")

class AuthRouteHandler(BaseHandler):
    def get(self):
        self.render("loginRegister.html")

class LoginHandler(BaseHandler):
    def get(self):
        self.render("blogHome.html")

    def post(self):
        self.render("blogHome.html")

class RegisterHandler(BaseHandler):
    def get(self):
        self.render("blogHome.html")

    def post(self):
        self.render("blogHome.html")

class ViewPostHandler(BaseHandler):
    def get(self):
        self.render("viewPost.html")

class CreatePostHandler(BaseHandler):
    def get(self):
        self.render("createEditPost.html")
