# main.py = main module for CatWiki

import datetime

from flask import request, redirect

import allpages
from allpages import *

import config

# pages:
import wiki
import sites

#---------------------------------------------------------------------

if __name__ == '__main__':
    print "Starting CatWiki..."
    app.run(port=config.PORT, debug=True, threaded=True)


#end
