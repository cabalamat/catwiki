# main.py = main module for sitebox

import datetime

from flask import request, redirect
from flask.ext.login import login_user, logout_user, current_user

import allpages
from allpages import *

import models

# pages:
import login
import wiki
import sites


#---------------------------------------------------------------------



#---------------------------------------------------------------------

if __name__ == '__main__':
    print "Starting SiteBox..."
    app.run(port=7330, debug=True)


#end
