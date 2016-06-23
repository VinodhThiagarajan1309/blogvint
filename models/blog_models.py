from google.appengine.ext import db

class User(db.Model):
	userid = db.StringProperty(required = True)
	password = db.StringProperty(required = True)
	emailId = db.StringProperty(required = False)
	created = db.DateTimeProperty(auto_now_add = True)

