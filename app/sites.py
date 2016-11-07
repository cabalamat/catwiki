# sites.py = site-level operations

import os.path, re

from flask import request, redirect

import markdown

from ulib import butil
from ulib.butil import form
from ulib.debugdec import prvars

import config
import allpages
from allpages import *

#---------------------------------------------------------------------

@app.route("/")
def front_page():
    return allSites()

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
    
    dirPan = wiki.getDirPan(siteName, "")
    fns, dirs = butil.getFilesDirs(dirPan)
    if butil.fileExists(butil.join(dirPan, "home.md")):
         homePageInfo = form("View <a href='/{siteName}/w/home'>"
             "<i class='fa fa-home'></i> home page</a>.",
             siteName = siteName)           
    else:                                
         homePageInfo = form("""There is no home page.
             <a href='/{siteName}/wikiedit/home'>
                <i class='fa fa-plus'></i>
                Create one</a>.""",
             siteName = siteName)  
         
    contents = """\
<h1>Information about site <i class='fa fa-bank'></i> {siteName}</h1>

<p><b>{siteName}</b> is stored in directory <code>{siteRoot}</code> .</p>

<p>There are {numPages} pages in the root folder, and {numSubDirs} sub-folders.
<a href='/{siteName}/w/'><i class='fa fa-folder'></i>
View root folder</a>.
</p>

<p>{homePageInfo}</p>
""".format(
        siteName = siteName,
        siteRoot = dirPan,
        numPages = len(fns),
        numSubDirs = len(dirs),
        homePageInfo = homePageInfo,
    )
    h = tem.render(
    
        siteName = siteName,
        title = "Information about " + siteName,
        nav2 = wiki.locationSitePath(siteName, ""),
        wikiText = contents,
    )
    return h 
    
#---------------------------------------------------------------------

#end
