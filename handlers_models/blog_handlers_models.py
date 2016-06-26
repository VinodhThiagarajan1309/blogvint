from base import BaseHandler
from util.blog_utils import *
from google.appengine.ext import db
import datetime

class User(db.Model):
    userid = db.StringProperty(required = True)
    password = db.StringProperty(required = True)
    email = db.StringProperty(required = False)
    created = db.DateTimeProperty(auto_now_add = True)
    firstname = db.StringProperty(required = True)
    lastname = db.StringProperty(required = True)

class Post(db.Model):
    title = db.TextProperty(required = True)
    content = db.TextProperty(required = True)
    user = db.ReferenceProperty(User, required=True)
    createdOn = db.DateTimeProperty(auto_now_add = True)
    updatedOn = db.DateTimeProperty(auto_now_add = True)

class PostComment(db.Model):
    comment = db.TextProperty(required = True)
    post = db.ReferenceProperty(Post, required=True)
    user = db.ReferenceProperty(User, required=True)
    createdOn = db.DateTimeProperty(auto_now_add = True)
    updatedOn = db.DateTimeProperty(auto_now_add = True)

class LikePost(db.Model):
    post = db.ReferenceProperty(Post, required=True)
    user = db.ReferenceProperty(User, required=True)
    createdOn = db.DateTimeProperty(auto_now_add = True)

'''Util Methods'''

def getLoggedInUserDetails(self):
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
                return userObj
            else:
                return False
        else:
            return False
    else:
        return False

def redirectToHomeScreen(self):
    self.redirect("/home")

def redirectToLoginScreen(self):
    self.redirect("/blogauth")
    

def signinAsGuest(self):
    listPosts = listAllPosts()
    self.render("blogHome.html",
                        role="guest",
                        listAllPosts=listPosts)

def listAllPosts():
    listAllPosts = db.GqlQuery("select * from Post order by updatedOn desc")
    prefetch_refprop(listAllPosts, Post.user)
    return listAllPosts

def prefetch_refprop(entities, prop):
    ref_keys = [prop.get_value_for_datastore(x) for x in entities]
    ref_entities = dict((x.key(), x) for x in db.get(set(ref_keys)))
    for entity, ref_key in zip(entities, ref_keys):
        prop.__set__(entity, ref_entities[ref_key])
        return entities

def listAllCommentsForPost(postkey):
    listAllComments = db.GqlQuery("select * from PostComment where post = KEY('"+str(postkey)+"') order by updatedOn desc")
    return listAllComments

def likesCountForPost(postkey):
    likes = db.GqlQuery("select * from LikePost where post = KEY('"+str(postkey)+"')")
    return likes.count()

def hasLikedPost(postkey,userkey):
    hasLikedPost = db.GqlQuery("select * from LikePost where post = KEY('"+str(postkey)+"') and user = KEY('"+str(userkey)+"')")
    print("******"+str(hasLikedPost.count()))
    return hasLikedPost.count()

''' This is where we decide the tabs to be shown to the user , we decide whether the user is a 
guest or member and render the flow accordingly'''

class MainHandler(BaseHandler):
    def get(self):
        userObj = getLoggedInUserDetails(self)
        if userObj :
            listPosts = listAllPosts()
            self.render("blogHome.html",
                role="member",
                member=userObj,
                listAllPosts=listPosts)
        else:
            signinAsGuest(self)


''' As we have designed a common screen for both login and registering we have this handler to render the same
based on Login and Register the user does from this screen he will be routed to Login or Register Handler respectively'''


class AuthRouteHandler(BaseHandler):
    def get(self):
        userObj = getLoggedInUserDetails(self)
        if userObj :
            self.redirect("/home")
        else:
            self.render("loginRegister.html")


''' The First time registering user enter this handlers post method , this is where we set the 
cookie for the first time for a registered user'''


class RegisterHandler(BaseHandler):
    def get(self):
        userObj = getLoggedInUserDetails(self)
        if userObj :
            self.redirect("/home")
        else:
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
                    str(userId)+"|"+str(passHash)+' Path=/')
                self.redirect("/home")


''' Returning User is directed by the app from Login screen to this Handlers post method.
This is where we set the cookie for the first time after validating the password. With Invalid
credentials the user is taken back to the login screen'''


class LoginHandler(BaseHandler):
    def get(self):
        userObj = getLoggedInUserDetails(self)
        if userObj :
            self.redirect("/home")
        else:
            self.redirect("/blogauth")

    def post(self):
        userid = self.request.get("inputUserId")
        password = self.request.get("inputPassword")
        #Chech if user name exists
        q = User.gql("WHERE userid = '"+str(userid)+"'");
        userObj = q.get()
        if userObj:
            if  valid_pw(userid, password, userObj.password):
                self.response.headers.add_header('Set-Cookie', 'user_id='+str(userObj.key().id())+"|"+str(userObj.password.split('|')[0])+' Path=/')
                self.redirect("/home")
            else:
                self.render("loginRegister.html" , invalidLogin=True)
        else:
            self.render("loginRegister.html" , invalidLogin=True)


''' To View a Post there are no conditons'''


class ViewPostHandler(BaseHandler):
    def get(self , postId):
        key = db.Key.from_path("Post" , int(postId))
        post = db.get(key)
        userObj = getLoggedInUserDetails(self)
        listComments = listAllCommentsForPost(key)
        likes = likesCountForPost(key)
        if(listComments.count() == 0):
            listComments = None
        if userObj :
            role = "member"
            member= userObj.firstname+" "+userObj.lastname
            hasLikedPostAlready = hasLikedPost(post.key(),userObj.key())
        else :
            role = "guest"
            member = None
            hasLikedPostAlready = None
        if userObj and userObj.key().id() == post.user.key().id():
            isPostAuthor = True
        else:
            isPostAuthor = False
        params = dict(role=role,
                       post=post,
                        member=userObj,
                        likes=likes,
                        listComments=listComments,
                        isPostAuthor=isPostAuthor,
                        hasLikedPostAlready=hasLikedPostAlready)

        self.render("viewPost.html", **params)


''' The user should be logged into the blog to achived this flow
    else the he will be directed to home screen as guest.
'''


class CreatePostHandler(BaseHandler):
    def get(self):
        userObj = getLoggedInUserDetails(self)
        if userObj :
            self.render("createEditPost.html",
                role="member",
                member=userObj)
        else :
            redirectToLoginScreen(self)

    def post(self):
        title = self.request.get("title")
        content = self.request.get("content")
        userObj = getLoggedInUserDetails(self)
        if userObj :
            postObj = Post(title=title,content=content,user=userObj)
            postObj.put()
            postId = postObj.key().id()
            self.redirect("/viewpost/"+str(postId))
        else :
            redirectToLoginScreen(self)


''' There are 2 conditions for this flow to work
    1) The User should be logged in to EDIT
    2) The User should be the Post owner to EDIT
    Only then allow , otherwise point him to home screen'''


class EditPostHandler(BaseHandler):
    def get(self , postId):
        userObj = getLoggedInUserDetails(self)
        postkey = db.Key.from_path("Post" , int(postId))
        post = db.get(postkey)
        if userObj and userObj.key().id() == post.user.key().id():
            self.render("createEditPost.html",
                role="member",
                member=userObj,
                post=post)
        else:
            redirectToLoginScreen(self)

    def post(self, postId):
        title = self.request.get("title")
        content = self.request.get("content")
        userObj = getLoggedInUserDetails(self)
        if userObj:
            key = db.Key.from_path("Post" , long(postId))
            postObj = db.get(key)
            postObj.title = title
            postObj.content = content
            postObj.updatedOn = datetime.datetime.now()
            postObj.put()
            postId = postObj.key().id()
            self.redirect("/viewpost/"+str(postId))
        else :
            redirectToLoginScreen(self)

class PostCommentHandler(BaseHandler):
    def post(self):
        userObj = getLoggedInUserDetails(self)
        comment = self.request.get("comment")
        postId = self.request.get("commentPostId")
        commentId = self.request.get("commentId")
        if userObj and len(commentId.strip()) > 0 :
            key = db.Key.from_path("PostComment" , long(commentId))
            postCommentObj = db.get(key)
            if userObj.key().id() == postCommentObj.user.key().id():
                postCommentObj.comment = comment
                postCommentObj.updatedOn = datetime.datetime.now()
                postCommentObj.put()
            else:
                redirectToLoginScreen(self)
        elif userObj:
            key = db.Key.from_path("Post" , long(postId))
            postObj = db.get(key)
            if postObj:
                postCommentObj = PostComment(comment=comment,post=postObj,user=userObj )
                postCommentObj.put()
        else:
            return redirectToLoginScreen(self)
        self.redirect("/viewpost/"+str(postId))

class DeleteCommentHandler(BaseHandler):
    def post(self):
        userObj = getLoggedInUserDetails(self)
        postId = self.request.get("commentPostId")
        commentId = self.request.get("commentId")
        key = db.Key.from_path("PostComment" , long(commentId))
        postCommentObj = db.get(key)
        if userObj and userObj.key().id() == postCommentObj.user.key().id():
            postCommentObj.delete()
        else:
            redirectToLoginScreen(self)
        self.redirect("/viewpost/"+str(postId))

class DeletePostHandler(BaseHandler):
    def post(self):
        userObj = getLoggedInUserDetails(self)
        postId = self.request.get("commentPostId")
        postkey = db.Key.from_path("Post" , int(postId))
        post = db.get(postkey)
        if userObj and userObj.key().id() == post.user.key().id():
            postComments = listAllCommentsForPost(post.key())
            commentKeys = []
            for comment in postComments:
                commentKeys.append(comment.key())
            db.delete(commentKeys)
            post.delete()
        redirectToHomeScreen(self)


class LikePostHandler(BaseHandler):
    def post(self):
        userObj = getLoggedInUserDetails(self)
        postId = self.request.get("postId")
        postkey = db.Key.from_path("Post" , int(postId))
        postObj = db.get(postkey)
        if userObj and postObj :
            likeObj = LikePost(post=postObj,user=userObj)
            likeObj.put()
            self.redirect("/viewpost/"+str(postId))
        else:
            redirectToLoginScreen(self)


class LogoutHandler(BaseHandler):
    def get(self):
        userObj = getLoggedInUserDetails(self)
        if userObj:
            self.response.headers.add_header('Set-Cookie', 'user_id=')
            self.redirect("/blogauth")
        else:
            self.redirect("/home")


