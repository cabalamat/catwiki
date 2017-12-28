# history.py

import os.path, datetime, time

from flask import request, redirect, Response

import git

from ulib import butil
from ulib.butil import form
from ulib.debugdec import prvars, pr

import allpages
from allpages import *

import wiki

#---------------------------------------------------------------------

def getRepo(siteName, pathName):
    """
    @param siteName::str
    @param pathName::str
    @return::Repo = a git repository
    """
    dp = wiki.getDirPan(siteName, "")
    prvars("dp")
    repo = git.Repo(dp)
    prvars("dp repo")
    return repo

#---------------------------------------------------------------------

@app.route("/<siteName>/history/<path:pathName>")
def history(siteName, pathName):
    pr("siteName=%r pathName=%r", siteName, pathName)
    tem = jinjaEnv.get_template("history.html")
    
    repo = getRepo(siteName, pathName)
    #lsf = repo.git.log(form("--follow {}.md", pathName))
    commits = list(repo.iter_commits(paths=pathName+".md"))
    prvars("commits")
    
    h = tem.render(
        title = pathName,
        siteName = siteName,
        pathName = pathName,
        nav2 = wiki.locationSitePath(siteName, pathName),
        table = getCommitsTable(pathName, commits)
    )
    return h

def getCommitsTable(pathName, commits):
    """
    @param commits::[git.Commit]
    @return::str containing html
    """
    h = """<table class='report_table'>
<tr> 
    <th>Date</th>
    <th>Author</th>
    <th>Message</th>
    <th>Size</th>
    <th>Hex SHA</th>
</tr>    
"""
    for co in commits:
        path = pathName+".md"
        fileData = (co.tree / path).data_stream.read()
        prvars("fileData")
        
        h += form("""<tr> 
    <td><tt>{date}</tt></td>
    <td>{author}</td>
    <td>{message}</td>
    <td>{size}</td>
    <td><tt>{hexsha}</tt></td>
</tr>""",
            date=niceTime(co.authored_date),
            author=co.author.name,
            message=htmlEsc(co.message),
            size=len(fileData),
            hexsha=co.hexsha,
        )    
    #//for co
    h += "</table>\n"
    return h
    
def niceTime(t):
    """ Converts a time in seconds since epoch to a nice string """
    nt = time.strftime("%Y-%b-%d %H:%M",
        time.gmtime(t))
    return htmlEsc(nt)

#---------------------------------------------------------------------


#end
