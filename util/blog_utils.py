import re
import hashlib
import hmac
import random
import string

def make_salt():
    return ''.join(random.choice(string.letters) for x in xrange(5))

# Implement the function valid_pw() that returns True if a user's password
# matches its hash. You will need to modify make_pw_hash.


def make_pw_hash(name, pw, salt=None):
    if not salt:
        salt = make_salt()
    h = hashlib.sha256(str(name) + str(pw) + str(salt)).hexdigest()
    return '%s|%s' % (h, salt)


def valid_pw(name, pw, h):
	print("**************"+h)
	salt = h.split('|')[1]
	return h == make_pw_hash(name, pw, salt)
