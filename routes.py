#!/usr/bin/env python
# -*- coding: utf-8 -*-

from handlers.login_register_handler import *

#This is the place where all of your URL mapping goes
route_list = [
	('/',MainHandler),
	('/blogauth',AuthRouteHandler),
	('/register',RegisterHandler),
	('/login',LoginHandler),
	('/viewpost',ViewPostHandler),
	('/createpost',CreatePostHandler)
	]
