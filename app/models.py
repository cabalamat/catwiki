# models.py for sitebox

"""
MongoDB tables defined in Mongoab will go here.
"""

import random

#import scrypt

import mongoab

from allpages import loginManager, jinjaEnv

#---------------------------------------------------------------------
# Users are stored in the user table

class User(mongoab.MonDoc):
    userName = mongoab.StrField()
    password = mongoab.StrField()
    hashedPassword = mongoab.StrField()
    email = mongoab.StrField()
    isAdmin = mongoab.BoolField(
        title="Is Admin?",
        desc="Does the user have privileges to administer the site?")

    _collection = mongoab.database.user

    #========== stuff Flask-login needs: ==========
    """ see
    <https://flask-login.readthedocs.org/en/latest/#your-user-class>
    """

    def is_authenticated(self):
        return self.has_key('_id')

    def is_active(self):
        return True

    def is_anonymous(self):
        return not self.has_key('_id')

    def get_id(self):
        return unicode(self.userName)

    #==========

    def preSave(self):
        """ We don't want to save the plaintext password to
        the database.
        """
        self.hashedPassword = hashPassword(self.password)
        self.password = "(hidden)"

@loginManager.user_loader
def load_user(userId):
    user = User.find_one({'userName': userId})
    # Note that if a user wasn't found, (user) will be None
    # here, which is what loginManager wants.

    return user


#---------- functions for encrypting passwords:

def randStr(length):
    return ''.join(chr(random.randint(0,255))
                   for i in range(length))

def hashPassword(password):
    encrypted = scrypt.encrypt(randStr(64), password, maxtime=0.05)
    hx = toHex(encrypted)
    return hx

def verifyPassword(hashedPassword, guessedPassword):
    try:
        scrypt.decrypt(fromHex(hashedPassword),
                       guessedPassword,
                       maxtime=0.05)
        return True
    except scrypt.error:
        return False

def toHex(s):
    """ convenrt a str to another str containing hex digits, e.g.
    '\xab' -> 'ab'
    """
    hexDigits = "0123456789abcdef"
    r = ""
    for ch in s:
        n = ord(ch)
        n1 = int(n/16)
        n2 = n - n1*16
        r += hexDigits[n1] + hexDigits[n2]
    return r

def fromHex(s):
    """ does the opposite of toHex """
    hexValues = {
        '0':0, '1':1, '2':2, '3':3,
        '4':4, '5':5, '6':6, '7':7,
        '8':8, '9':9, 'a':10, 'b':11,
        'c':12, 'd':13, 'e':14, 'f':15
    }
    r = ""
    for c1, c2 in zip(s[::2], s[1:][::2]):
        v = hexValues[c1]*16 + hexValues[c2]
        r += chr(v)
    return r


#---------------------------------------------------------------------
""" a class demonstrating the capabilities of mongoab """

class Foo(mongoab.MonDoc):
    name = mongoab.StrField(
        desc="the name of the document",
        minLength=1)
    typeHere = mongoab.TextAreaField(
        desc="a TextAreaField",
        default="text goes here")
    favouriteAnimal = mongoab.ChoiceField(
        choices = (('C', 'Cat'),
                   ('D', 'Dog'),
                   ('S', 'Spider')))
    postcode = mongoab.PostcodeField()
    tickyBox = mongoab.BoolField()
    numBoxes = mongoab.IntField(
        desc="an IntField")
    topSpeed = mongoab.FloatField(
        desc="top speed on mph")
    startTime = mongoab.HhmmssField()
    finishTime = mongoab.HhmmssField()



#---------------------------------------------------------------------





#end
