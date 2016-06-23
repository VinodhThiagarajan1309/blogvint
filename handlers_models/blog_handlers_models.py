from base import BaseHandler
from util.blog_utils import *
from google.appengine.ext import db

class User(db.Model):
    userid = db.StringProperty(required = True)
    password = db.StringProperty(required = True)
    email = db.StringProperty(required = False)
    created = db.DateTimeProperty(auto_now_add = True)
    firstname = db.StringProperty(required = True)
    lastname = db.StringProperty(required = True)


class MainHandler(BaseHandler):
    def get(self):
        userIdHash = self.request.cookies.get("user_id")
        if userIdHash and  userIdHash.find('|') != -1 :
            userId = userIdHash.split('|')[0]
            userHash_W_O_Salt_from_cookie = userIdHash.split('|')[1]
            key = db.Key.from_path("User" , long(userId))
            userObj = db.get(key)
            if userObj:
                passFromDB = userObj.password
                hashFromDB = passFromDB.split('|')[0]
                if userHash_W_O_Salt_from_cookie == hashFromDB :
                    self.render("blogHome.html",
                        role="member",
                        memberName=userObj.firstname+" "+userObj.lastname)
                else:
                    self.signinAsGuest()
            else:
                self.signinAsGuest()
        else :
            self.signinAsGuest()

    def signinAsGuest(self):
        self.render("blogHome.html",role="guest")

class AuthRouteHandler(BaseHandler):
    def get(self):
        self.render("loginRegister.html")

class RegisterHandler(BaseHandler):
    def get(self):
        self.redirect("/blogauth")

    def post(self):
        firstname = self.request.get("firstName")
        lastname = self.request.get("lastName")
        userid = self.request.get("userId")
        password = self.request.get("password")
        email = self.request.get("email")

        # Check if user name exists
        q = User.gql("WHERE userid = '"+str(userid)+"'")
        user = q.get()
        if user:
            params = dict(
                userAlreadyExists=True,
                userId=userid,
                email=email,
                firstName=firstname,
                lastName=lastname)
            self.render("loginRegister.html", **params)
        else:
            passHashWSalt = make_pw_hash(userid, password)
            passHash = passHashWSalt.split('|')[0]
            userObj = User(
                userid=userid, 
                password=passHashWSalt, 
                email=email,
                firstname=firstname,
                lastname=lastname)
            userObj.put()
            userId = userObj.key().id()

            if userId:
                self.response.headers.add_header(
                    'Set-Cookie',
                    'user_id=' +
                    str(userId)+"|"+str(passHash)+' Path=/welcome')
                self.redirect("/home")


class LoginHandler(BaseHandler):
    def get(self):
        self.redirect("/blogauth")

    def post(self):
        userid = self.request.get("inputUserId")
        password = self.request.get("inputPassword")
        #Chech if user name exists
        q = User.gql("WHERE userid = '"+str(userid)+"'");
        userObj = q.get()
        if userObj:
            if  valid_pw(userid, password, userObj.password):
                self.response.headers.add_header('Set-Cookie', 'user_id='+str(userObj.key().id())+"|"+str(userObj.password.split('|')[0])+' Path=/welcome')
                self.redirect("/home")
            else:
                self.render("loginRegister.html" , invalidLogin=True)
        else:
            self.render("loginRegister.html" , invalidLogin=True)

class ViewPostHandler(BaseHandler):
    def get(self):
        self.render("viewPost.html")

class CreatePostHandler(BaseHandler):
    def get(self):
        self.render("createEditPost.html")
