# imports for this module
from base import BaseHandler
from util.blog_utils import *
from google.appengine.ext import db
import datetime

'''User model for Login and Validation purposes'''


class User(db.Model):
    userid = db.StringProperty(required=True)
    password = db.StringProperty(required=True)
    email = db.StringProperty(required=False)
    created = db.DateTimeProperty(auto_now_add=True)
    firstname = db.StringProperty(required=True)
    lastname = db.StringProperty(required=True)

''' Post storage Model '''


class Post(db.Model):
    title = db.TextProperty(required=True)
    content = db.TextProperty(required=True)
    user = db.ReferenceProperty(User, required=True)
    createdOn = db.DateTimeProperty(auto_now_add=True)
    updatedOn = db.DateTimeProperty(auto_now_add=True)

''' Comment storage model'''


class PostComment(db.Model):
    comment = db.TextProperty(required=True)
    post = db.ReferenceProperty(Post, required=True)
    user = db.ReferenceProperty(User, required=True)
    createdOn = db.DateTimeProperty(auto_now_add=True)
    updatedOn = db.DateTimeProperty(auto_now_add=True)

''' Likes storage model'''


class LikePost(db.Model):
    post = db.ReferenceProperty(Post, required=True)
    user = db.ReferenceProperty(User, required=True)
    createdOn = db.DateTimeProperty(auto_now_add=True)

# Get all the posts


def listAllPosts():
    listAllPosts = db.GqlQuery("select * from Post order by updatedOn desc")
    prefetch_refprop(listAllPosts, Post.user)
    return listAllPosts

# http://blog.notdot.net/2010/01/ReferenceProperty-prefetching-in-App-Engine


def prefetch_refprop(entities, prop):
    ref_keys = [prop.get_value_for_datastore(x) for x in entities]
    ref_entities = dict((x.key(), x) for x in db.get(set(ref_keys)))
    for entity, ref_key in zip(entities, ref_keys):
        prop.__set__(entity, ref_entities[ref_key])
        return entities

# List all the comments for the given post


def listAllCommentsForPost(postkey):
    listAllComments = db.GqlQuery(
        "select * from PostComment where post = " +
        "KEY('" + str(postkey) + "') order by updatedOn desc")
    return listAllComments

# Count the Likes for the post


def likesCountForPost(postkey):
    likes = db.GqlQuery(
        "select * from LikePost where post = KEY('" + str(postkey) + "')")
    return likes.count()

# Has the user already liked the post


def hasLikedPost(postkey, userkey):
    hasLikedPost = db.GqlQuery("select * from LikePost where post = KEY('" +
                               str(postkey) + "') and user = KEY('" +
                               str(userkey) + "')")
    return hasLikedPost.count()


''' To ensure if the user has logged in and the credentials are correct before
doing any create,update or delete operations'''


def getLoggedInUserDetails(self):
    # Get the user cookie
    userIdHash = self.request.cookies.get("user_id")
    # If the user cookie is present
    if userIdHash and userIdHash.find('|') != -1:
        # Get the user from the cookie
        userId = userIdHash.split('|')[0]
        # Get the hash from cookie
        userHash_W_O_Salt_from_cookie = userIdHash.split('|')[1]
        # Get the user obj from db
        key = db.Key.from_path("User", long(userId))
        userObj = db.get(key)
        # If the User Obj is present
        if userObj:
            passFromDB = userObj.password
            hashFromDB = passFromDB.split('|')[0]
            # If the cookie hash is same as hash from DB
            if userHash_W_O_Salt_from_cookie == hashFromDB:
                return userObj
            else:
                return False
        else:
            return False
    else:
        return False

# Redirect to Home screen


def redirectToHomeScreen(self):
    self.redirect("/home")

# Redirect to Login screen


def redirectToLoginScreen(self):
    self.redirect("/blogauth")

# Redirect to view screen


def redirectToViewScreen(self, postId):
    self.redirect("/viewpost/" + str(postId))

# Render blog home to the render


def signinAsGuest(self):
    listPosts = listAllPosts()
    self.render("blogHome.html",
                role="guest",
                listAllPosts=listPosts)

''' This is where we decide the tabs to be shown to the user , we decide
whether the user is a guest or member and render the flow accordingly'''


class MainHandler(BaseHandler):

    def get(self):
        userObj = getLoggedInUserDetails(self)
        if userObj:
            listPosts = listAllPosts()
            self.render("blogHome.html",
                        role="member",
                        member=userObj,
                        listAllPosts=listPosts)
        else:
            signinAsGuest(self)


''' As we have designed a common screen for both login and registering we have
this handler to render the samebased on Login and Register the user does from
this screen he will be routed to Login or Register Handler respectively'''


class AuthRouteHandler(BaseHandler):

    def get(self):
        userObj = getLoggedInUserDetails(self)
        if userObj:
            redirectToHomeScreen(self)
        else:
            self.render("loginRegister.html")


''' The First time registering user enter this handlers post method , this is
where we set the cookie for the first time for a registered user'''


class RegisterHandler(BaseHandler):

    def get(self):
        userObj = getLoggedInUserDetails(self)
        if userObj:
            self.redirect("/home")
        else:
            self.redirect("/blogauth")

    def post(self):
        # Get the parameters from the request
        firstname = self.request.get("firstName")
        lastname = self.request.get("lastName")
        userid = self.request.get("userId")
        password = self.request.get("password")
        email = self.request.get("email")

        # Check if user name exists
        q = User.gql("WHERE userid = '" + str(userid) + "'")
        user = q.get()
        # Error out the request if the user id already exists
        if user:
            params = dict(
                userAlreadyExists=True,
                userId=userid,
                email=email,
                firstName=firstname,
                lastName=lastname)
            self.render("loginRegister.html", **params)
        # Hash the userid , password and a random salt and store the User to DB
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
            # Set the Cookie for the newly registered User
            if userId:
                self.response.headers.add_header(
                    'Set-Cookie',
                    'user_id=' +
                    str(userId) + "|" + str(passHash) + ' Path=/')
                self.redirect("/home")


''' Returning User is directed by the app from Login screen to this Handlers
post method.This is where we set the cookie for the first time after validating
the password. With Invalidcredentials the user is taken back to the
login screen'''


class LoginHandler(BaseHandler):

    def get(self):
        userObj = getLoggedInUserDetails(self)
        # If the user is already logged in
        if userObj:
            self.redirect("/home")
        # If the user needs to login
        else:
            self.redirect("/blogauth")

    def post(self):
        userid = self.request.get("inputUserId")
        password = self.request.get("inputPassword")
        q = User.gql("WHERE userid = '" + str(userid) + "'")
        userObj = q.get()
        if userObj:
            # If the credentials are valid then set the cookie
            if valid_pw(userid, password, userObj.password):
                self.response.headers.add_header(
                    'Set-Cookie', 'user_id=' +
                    str(userObj.key().id()) + "|" +
                    str(userObj.password.split('|')[0]) + ' Path=/')
                self.redirect("/home")
            # Error out for invalid credentials
            else:
                self.render("loginRegister.html", invalidLogin=True)
        # Error out for invalid user id
        else:
            self.render("loginRegister.html", invalidLogin=True)


''' To View a Post there are no conditons'''


class ViewPostHandler(BaseHandler):

    def get(self, postId):
        userObj = getLoggedInUserDetails(self)
        key = db.Key.from_path("Post", int(postId))
        post = db.get(key)
        # Handling likes
        listComments = listAllCommentsForPost(key)
        likes = likesCountForPost(key)
        # Set the likes count
        if(listComments.count() == 0):
            listComments = None
        # If valid user viewing valid post
        if userObj and post:
            role = "member"
            member = userObj.firstname + " " + userObj.lastname
            hasLikedPostAlready = hasLikedPost(post.key(), userObj.key())
        else:
            role = "guest"
            member = None
            hasLikedPostAlready = None
        # Is User the author of this post
        if userObj and post and userObj.key().id() == post.user.key().id():
            isPostAuthor = True
        else:
            isPostAuthor = False
        # Build the param dict to be sent to screen
        params = dict(role=role,
                      post=post,
                      member=userObj,
                      likes=likes,
                      listComments=listComments,
                      isPostAuthor=isPostAuthor,
                      hasLikedPostAlready=hasLikedPostAlready)
        # Render the post
        self.render("viewPost.html", **params)


''' The user should be logged into the blog to achived this flow
    else the he will be directed to home screen as guest.
'''


class CreatePostHandler(BaseHandler):

    def get(self):
        userObj = getLoggedInUserDetails(self)
        # If logged in user
        if userObj:
            self.render("createEditPost.html",
                        role="member",
                        member=userObj)
        else:
            redirectToLoginScreen(self)

    def post(self):
        title = self.request.get("title")
        content = self.request.get("content")
        userObj = getLoggedInUserDetails(self)
        # If logged in user
        if userObj:
            postObj = Post(title=title, content=content, user=userObj)
            postObj.put()
            postId = postObj.key().id()
            redirectToViewScreen(self, postId)
        else:
            redirectToLoginScreen(self)


''' There are 2 conditions for this flow to work
    1) The User should be logged in to EDIT
    2) The User should be the Post owner to EDIT
    Only then allow , otherwise point him to home screen'''


class EditPostHandler(BaseHandler):

    def get(self, postId):
        userObj = getLoggedInUserDetails(self)
        postkey = db.Key.from_path("Post", int(postId))
        post = db.get(postkey)
        # If valid user and post author proceed to edit
        if userObj and userObj.key().id() == post.user.key().id():
            self.render("createEditPost.html",
                        role="member",
                        member=userObj,
                        post=post)
        else:
            redirectToLoginScreen(self)

    def post(self, postId):
        userObj = getLoggedInUserDetails(self)
        # Get the parameters from the request
        title = self.request.get("title")
        content = self.request.get("content")
        key = db.Key.from_path("Post", long(postId))
        postObj = db.get(key)
        # If valid user and post author allow edit
        if userObj and userObj.key().id() == postObj.user.key().id():
            postObj.title = title
            postObj.content = content
            postObj.updatedOn = datetime.datetime.now()
            postObj.put()
            postId = postObj.key().id()
            redirectToViewScreen(self, postId)
        else:
            redirectToLoginScreen(self)

''' Post comment '''


class PostCommentHandler(BaseHandler):

    def post(self):
        userObj = getLoggedInUserDetails(self)
        # Get the parameters from the request
        comment = self.request.get("comment")
        postId = self.request.get("commentPostId")
        commentId = self.request.get("commentId")
        # If the user is valid and comment id is present , its an update
        if userObj and len(commentId.strip()) > 0:
            key = db.Key.from_path("PostComment", long(commentId))
            postCommentObj = db.get(key)
            # If the user is the owner of the comment then allow update
            if userObj.key().id() == postCommentObj.user.key().id():
                postCommentObj.comment = comment
                postCommentObj.updatedOn = datetime.datetime.now()
                postCommentObj.put()
            # If valid user but not comment owner goback to viewpost
            else:
                redirectToViewScreen(self, postId)
        # If the user is valid and post comment then its a new comment
        elif userObj:
            key = db.Key.from_path("Post", long(postId))
            postObj = db.get(key)
            if postObj:
                postCommentObj = PostComment(
                    comment=comment, post=postObj, user=userObj)
                postCommentObj.put()
        # If not logged in
        else:
            return redirectToLoginScreen(self)
        redirectToViewScreen(self, postId)

''' Delete Comment Handler'''


class DeleteCommentHandler(BaseHandler):

    def post(self):
        userObj = getLoggedInUserDetails(self)
        # Get the parameters from the request
        postId = self.request.get("commentPostId")
        commentId = self.request.get("commentId")
        key = db.Key.from_path("PostComment", long(commentId))
        postCommentObj = db.get(key)
        # If valid user and author of the comment then delete it
        if userObj and userObj.key().id() == postCommentObj.user.key().id():
            postCommentObj.delete()
        else:
            redirectToLoginScreen(self)
        redirectToViewScreen(self, postId)

''' Delete Post and Comments Related to it.'''


class DeletePostHandler(BaseHandler):

    def post(self):
        userObj = getLoggedInUserDetails(self)
        # Get the parameters from the request
        postId = self.request.get("commentPostId")
        postkey = db.Key.from_path("Post", long(postId))
        post = db.get(postkey)
        # If valid user and is post's author
        if userObj and userObj.key().id() == post.user.key().id():
            # Fetch and delete the comments for the given post
            postComments = listAllCommentsForPost(post.key())
            commentKeys = []
            for comment in postComments:
                commentKeys.append(comment.key())
            db.delete(commentKeys)
            # Delete the post
            post.delete()
            # Go back to blog home
            redirectToHomeScreen(self)
        else:
            redirectToLoginScreen(self)

''' Handle Likes'''


class LikePostHandler(BaseHandler):

    def post(self):
        userObj = getLoggedInUserDetails(self)
        # Get the parameters from the request
        postId = self.request.get("postId")
        postkey = db.Key.from_path("Post", long(postId))
        postObj = db.get(postkey)
        # If the user is logged in and its a valid then log the like
        if userObj and postObj:
            likeObj = LikePost(post=postObj, user=userObj)
            likeObj.put()
            redirectToViewScreen(self, postId)
        else:
            redirectToLoginScreen(self)

''' Handle App logout '''


class LogoutHandler(BaseHandler):

    def get(self):
        # Logout only if the user is logged in
        userObj = getLoggedInUserDetails(self)
        if userObj:
            self.response.headers.add_header('Set-Cookie', 'user_id=')
            redirectToLoginScreen(self)
        else:
            redirectToHomeScreen(self)
