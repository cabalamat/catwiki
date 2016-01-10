#!/usr/bin/env python

"""
mkadmin.py = make an admin user for mongoab projects.
This version for sitebox.
"""

import argparse

import mongoab; mongoab.setDatabase('sitebox')

import models

#---------------------------------------------------------------------

def userExists(userName):
    theUser = models.User.find_one({'userName': userName})
    if theUser==None: return False
    return True

def makeAdmin(userName, password):
    """ make a new admin user """
    newUser = models.User()
    newUser.userName = userName
    newUser.password = password
    newUser.isAdmin = True
    newUser.save()

#---------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("userName",
        help="the user name for the new admin user")
    parser.add_argument("password",
        help="the new user's password")

    args = parser.parse_args()

    if userExists(args.userName):
        print "User '{}' already exists, so cannot be created.".format(
            args.userName)
    else:
        makeAdmin(args.userName, args.password)
        print "User created."
    print "Admin users are:"
    adminUsers = list(models.User.find({'isAdmin':True}))
    adminUsers.sort(key=lambda x: x.userName)
    for au in adminUsers:
        print au.userName

if __name__=='__main__':
    main()

#end
