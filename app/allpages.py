# allpages.py = stuff relevant to all pages

import os.path
import collections
import cgi

import config

from flask import Flask, request
app = Flask(__name__)
#app.config["SECRET_KEY"] = "don't tell anyone" # not using
app.config["SESSION_COOKIE_NAME"] = "session_%d" % (config.PORT,)
app.config["WERKZEUG_DEBUG_PIN"] = "off"

from ulib import debugdec, butil, termcolours
from ulib.debugdec import printargs, prvars

#---------------------------------------------------------------------
# jinja2 environment

import jinja2
from jinja2 import Template

jinjaEnv = jinja2.Environment()
thisDir = os.path.dirname(os.path.realpath(__file__))
templateDir = butil.join(thisDir, "templates")
jinjaEnv.loader = jinja2.FileSystemLoader(templateDir)


#---------------------------------------------------------------------
# login manager

def helpPage():
    p = request.path[1:]
    r = p.split('/')[0]
    if r=="": r = "main"
    return r
jinjaEnv.globals['helpPage'] = helpPage

def highlightPageIfCurrent(testUrl):
    """ If the current page starts with (testUrl), highlight it
    by returning the code " class='active'".
    Otherwise return ""
    """
    p = request.path.lstrip("/")
    if p.startswith(testUrl): return " class='active'"
    return ""

jinjaEnv.globals['hpic'] = highlightPageIfCurrent

#---------------------------------------------------------------------
# utility functions

def form(s, *args, **kwargs):
    return s.format(*args, **kwargs)

def minToHMS(m):
    """ convert a time in minutes into hh:mm:ss
    @param m [int|float]
    @return [str]
    """
    mn = m % 60
    hr = int(m/60.0)
    mn = m - hr*60
    mn2 = int(mn)
    sc = int((mn-mn2)*60)
    r = "{:d}:{:02d}:{:02d}".format(hr, mn2, sc)
    return r

def htmlEscape(s):
    return cgi.escape(s)
htmlEsc = htmlEscape

#---------------------------------------------------------------------

#end
