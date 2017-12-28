# history.py

import os.path, datetime

from flask import request, redirect, Response

from ulib import butil
from ulib.butil import form
from ulib.debugdec import prvars, pr

import allpages
from allpages import *

import wiki

#---------------------------------------------------------------------

@app.route("/<siteName>/history/<path:pathName>")
def history(siteName, pathName):
    pr("siteName=%r pathName=%r", siteName, pathName)
    tem = jinjaEnv.get_template("history.html")
    
    h = tem.render(
        title = pathName,
        siteName = siteName,
        pathName = pathName,
        nav2 = wiki.locationSitePath(siteName, pathName),
    )
    return h













#---------------------------------------------------------------------


#end
