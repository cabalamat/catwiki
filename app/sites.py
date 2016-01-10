# sites.py = site-level operations

import os.path, re

from flask import request, redirect

import markdown

from ulib import butil
from ulib.debugdec import prvars

import config
import allpages
from allpages import *

#---------------------------------------------------------------------

@app.route("/_allSites")
def allSites():
    """ List all the sites for this SiteBox installation
    """
    tem = jinjaEnv.get_template("generic_10_2.html")
    contents = """\
<h1>List of all sites</h1>

{siteList}
""".format(siteList=siteListH())
    h = tem.render(   
        title = "All sites",
        nav2 = "<span class='loc-sitename'><a href='/_allSites'>"
            "<i class='fa fa-bank'></i></a>",
        wikiText = contents,
    )
    return h 

def siteListH():
    """ return HTML containing a list of sites 
    @return::str
    """
    h = "<p>\n"
    for stub in config.SITE_STUBS:
        _, dirs = butil.getFilesDirs(stub)
        for siteName in dirs:
            h += (("<span class='loc-sitename'><a href='/{siteName}/info'><i class='fa fa-bank'></i> {siteName}</a></span> -- under <code>{stub}</code><br>\n")
                .format(siteName=siteName,
                        stub=stub))     
        #//for siteName
    #//for stub   
    h += "</p>\n"
    return h        
        
    
@app.route("/<siteName>/info")
def siteInfo(siteName):
    """ Display information about a site.
    """
    import wiki
    
    tem = jinjaEnv.get_template("generic_10_2.html")
    contents = """\
<h1>Information about site <i class='fa fa-bank'></i> {siteName}</h1>
""".format(siteName = siteName)
    h = tem.render(
    
        siteName = siteName,
        title = "Information about " + siteName,
        nav2 = wiki.locationSitePath(siteName, ""),
        wikiText = contents,
    )
    return h 
    
#---------------------------------------------------------------------

#end
