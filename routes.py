#!/usr/bin/env python
# -*- coding: utf-8 -*-

from handlers_models.blog_handlers_models import *

#This is the place where all of your URL mapping goes
route_list = [
	('/',MainHandler),
	('/blogauth',AuthRouteHandler),
	('/register',RegisterHandler),
	('/login',LoginHandler),
	(r'/viewpost/(\d+)',ViewPostHandler),
	('/createpost',CreatePostHandler),
	(r'/editpost/(\d+)',EditPostHandler),
	('/home',MainHandler),
	('/postcomment',PostCommentHandler),
	('/logout',LogoutHandler),
	('/deletecomment',DeleteCommentHandler),
	('/deletepost',DeletePostHandler),
	('/likepost',LikePostHandler)
	]
