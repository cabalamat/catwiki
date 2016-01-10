# wiki.py

import os.path, re, math, inspect, datetime, sys

from flask import request, redirect, Response

import markdown

from ulib import butil
from ulib.butil import form
from ulib.debugdec import prvars, pr

import config
import allpages
from allpages import *


#---------------------------------------------------------------------
# debugging

def prt(formatStr="", *args):
    """ print a message, prepended with timestamp, function, line
    number. Uses old-style '%' format strings.
    @param formatStr::str
    @param args::[]
    """
    now = datetime.datetime.now()
    nowStr = now.strftime("%H:%M:%S.%f")
    caller = inspect.stack()[1]
    fileLine = caller[2]
    functionName = caller[3]

    if len(args)>0:
        s = formatStr % args
    else:
        s = formatStr
    t = "%s %s():%d: " % (nowStr, functionName, fileLine)
    sys.stderr.write(t + s + "\n")

#---------------------------------------------------------------------

@app.route("/<siteName>/w/")
def wikiPageEmptyPath(siteName):
    return wikiPage(siteName, "")

#---------------------------------------------------------------------

@app.route("/<siteName>/w/<path:pathName>")
def wikiPage(siteName, pathName):
    mimeType = getMimeType(pathName)
    if mimeType:
        pan = getDirPan(siteName, pathName)
        data = open(pan).read()
        return Response(data, mimetype=mimeType)

    if pathName=="" or pathName[-1:]=="/":
        tem = jinjaEnv.get_template("wiki_index.html")
        title, contents = getIndex(siteName, pathName)
    else:
        tem = jinjaEnv.get_template("wiki_page.html")
        title, contents = getArticleBody(siteName, pathName)

    h = tem.render(
        title = title,
        siteName = siteName,
        pathName = pathName,
        nav2 = locationSitePath(siteName, pathName),
        wikiText = contents,
    )
    return h

MIME_TYPES = [
   ('pdf', 'application/pdf'),
   ('gif', 'image/gif'),
   ('png', 'image/png'),
   ('jpg', 'image/jpeg'),
   ('jpeg', 'image/jpeg'),
]

def getMimeType(pathName):
    """ Get the mime type of a pathname
    @param pathName::str
    @return::str containing mime type, or "" if none.
    """
    pnl = pathName.lower()
    for ext, mt in MIME_TYPES:
        ext2 = "." + ext
        if pnl[-len(ext2):]==ext2:
            return mt
    #//for
    return ""

#---------------------------------------------------------------------

@app.route("/<siteName>/wikiedit/<path:pathName>", methods=['POST', 'GET'])
def wikiedit(siteName, pathName):
    prt("siteName=%r pathName=%r", siteName, pathName)
    tem = jinjaEnv.get_template("wikiedit.html")

    if pathName=="" or pathName[-1:]=="/":
        # can't edit directories
        return redirect("/{siteName}/w/{pathName}".format(
                siteName = siteName,
                pathName = pathName,
            ), 301)
    else:
        source = getArticleSource(siteName, pathName)
        if source == "":
            source = "# " + pathName + "\n"
    if request.method=='POST':
        if request.form['delete'] == "1":
            # delete this article
            deleteArticle(siteName, pathName)
            articleDirectory = getArticleDirname(pathName)
            return redirect("/{siteName}/w/{pathName}".format(
                    siteName = siteName,
                    pathName = articleDirectory,
                 ), 303)
        else:
            newSource = request.form['source']
            prvars("newSource")
            saveArticleSource(siteName, pathName, newSource)
            return redirect("/{siteName}/w/{pathName}".format(
                    siteName = siteName,
                    pathName = pathName,
                 ), 303)
    #//if
    title = pathName

    h = tem.render(
        title = title,
        siteName = siteName,
        pathName = pathName,
        nav2 = locationSitePath(siteName, pathName),
        source = source,
    )
    prt("response length %d", len(h))
    return h

#---------------------------------------------------------------------

def pathJoin(sp, ix):
    return "/".join(sp[0:ix+1])

def locationSitePath(siteName, pathName):
    """ return html containing links for a wiki path
    @param siteName::str
    @param pathName::str
    @return::str, containing HTML
    """

    useForDir = "<i class='fa fa-folder-open'></i>"
    #useForDir = "<i class='fa fa-chevron-right'></i>"
    #useForDir = "<b>/</b>"
    sp = pathName.split("/")
    h = ("<span class='loc-sitename'><a href='/_allSites'>"
         "<i class='fa fa-bank'></i></a>"
         "<a href='/{siteName}/info'>{siteName}</a></span>").format(
        siteName=siteName)
    h += ("\n<span class='loc-wiki-path'><a href='/%s/w/'>%s</a>"
         % (siteName, useForDir))
    prvars("pathName sp")
    for ix, part in enumerate(sp):
        item = ("<a href='/%s/w/%s'>%s</a>"
            %(siteName, pathJoin(sp,ix), part))
        if ix<len(sp)-1:
            item += ("<a href='/%s/w/%s/'>%s</a>"
                %(siteName, pathJoin(sp,ix), useForDir))
        h += item
    #//for
    h += "</span>"
    return h

def getArticleDirname(pathName):
    """ move up to an article's directory """
    sp = pathName.split("/")
    upOne = "/".join(sp[:-1]) + "/"
    return upOne

def deleteArticle(siteName, pathName):
    """ delete an article """
    pan = getDirPan(siteName, pathName)
    if pan:
        os.remove(pan + ".md")

#---------------------------------------------------------------------

markdownProcessor = markdown.Markdown(['extra', 'toc',
    'sane_lists',
    'codehilite(guess_lang=False)',
    #'wikilinks(base_url=,end_url=)',
    ])

def md(s):
    """ Convert markdown to html

    Uses the Python Markdown library to do this.
    See: <http://packages.python.org/Markdown/>
    """
    h = markdownProcessor.convert(s)
    return h

def convertQuickLinks(s):
    """ Converts [[xxx]] -> [xxx](xxx)
    NB: we are no longer using this, we're using the wikilinks
    extension instead.

    @param s [str] containing markdown source
    @return [str]
    """
    QUICKLINK_RE = r"\[\[([A-Za-z0-9_ -]+)\]\]"
    REPLACE_WITH = r"[\1](\1)"
    r = re.sub(QUICKLINK_RE, REPLACE_WITH, s)
    return r

def getArticlePan(siteName, pathName):
    """ return the pathname for an article
    @param siteName::str = the site name
    @param pathName::str = the pathname withing the site
    @return::str = the full pathname to the article (which may or may
        not exist). If the site doesn't exist, returns "".
    """
    if not siteName: return ""
    for stub in config.SITE_STUBS:
        _, dirs = butil.getFilesDirs(stub)
        if siteName in dirs:
            return butil.join(stub, siteName, pathName + ".md")
    #//for
    return ""

def getDirPan(siteName, pathName):
    """ return the pathname for a directory
    @param siteName::str = the site name
    @param pathName::str = the pathname within the site
    @return::str = the full pathname to the directory (which may or may
        not exist). If the site doesn't exist, returns "".
    """
    if not siteName: return ""
    for stub in config.SITE_STUBS:
        _, dirs = butil.getFilesDirs(stub)
        if siteName in dirs:
            return butil.join(stub, siteName, pathName)
    #//for
    return ""

def saveArticleSource(siteName, pathName, source):
    #pr("saving article %s:[%s] -----BODY:-----\n%s\n-----END-----",
    #    siteName, pathName, source)
    articlePan = getArticlePan(siteName, pathName)
    butil.writeFileUtf8(articlePan, source)

def getArticleSource(siteName, pathName):
    articlePan = getArticlePan(siteName, pathName)
    if butil.fileExists(articlePan):
        src = butil.readFileUtf8(articlePan)
        return src
    else:
        return ""

def getArticleBody(siteName, pathName):
    """ given an article name, return the body of the article.
    @return ::(str,str) =title,html
    """
    articlePan = getArticlePan(siteName, pathName)
    #prvars()
    if butil.fileExists(articlePan):
        src = butil.readFileUtf8(articlePan)
        src = convertQuickLinks(src)
        contents = md(src)
        return pathName, contents
    else:
        h = form("<p>({pathName} does not exist; "
            "<a href='/{siteName}/wikiedit/{pathName}'>create it</a>)</p>\n",
            siteName = htmlEscape(siteName),
            pathName = htmlEscape(pathName))
        return (pathName, h)


def getIndex(siteName, pathName):
    """ get an index of a directory.
    @param siteName::str
    @param pathName::str
    @return::(str,str) =title,html
    """
    def isArticle(fn):
        """ is a filename an article? """
        return (fn[-3:]==".md" and not fn[:1]=="~")


    if pathName[-1:] == "/":
        uPath = pathName[:-1]
    else:
        uPath = pathName
    dirPan = getDirPan(siteName, uPath)
    #prvars()
    if not os.path.isdir(dirPan):
        h = "<p>Directory {} does not exist.</p>\n".format(pathName)
        return h

    fns, dirs = butil.getFilesDirs(dirPan)
    dirs = [d for d in dirs if d[:1] != "."]
    arts = sorted([fn[:-3]
                  for fn in fns
                  if isArticle(fn)])
    nonArticles = sorted([fn
                  for fn in fns
                  if not isArticle(fn)])
    dirs = sorted(dirs)
    h = ("<h1><i class='fa fa-list'></i> Index of articles in "
         " /{}</h1>\n").format(pathName)
    items = []
    nonArticleItems = []
    if arts:
        for fn in arts:
            items.append("<a href='{fn}'>"
                "<i class='fa fa-file-text-o'></i> "
                "{fn}</a> - {text}".format(
                fn = fn,
                text = getTitle(butil.join(dirPan, fn+".md"))
            ))
        #//for
        h += bsColumns(items, 3)
    if nonArticles:
        for fn in nonArticles:
            nonArticleItems.append("<a href='{fn}'>"
                "<i class='fa fa-file-o'></i> "
                "{fn}</a>".format(
                fn = fn))
        #//for
        h += "<h3>Other files</h3>\n" + bsColumns(nonArticleItems, 3)
    if dirs:
        dirItems = []
        for d in dirs:
            dirItems.append(("<a href='{d}/'><i class='fa fa-folder'></i> "
                  "{text}</a>").format(
                d = d,
                text = d,
            ))
        #//for
        h += "<h3>Folders</h3>\n" + bsColumns(dirItems, 3)

    title = "Index of {}".format(pathName)
    return title, h

def getTitle(pan):
    """ get the title of an article
    @param pan [str] full pathname to the article
    """
    src = butil.readFile(pan).decode('utf-8', 'ignore')
    lines = src.split("\n")
    if len(lines)==0: return ""
    t = md(convertQuickLinks(lines[0].strip(" #")))
    if t.startswith("<p>"): t = t[3:]
    if t.endswith("</p>"): t = t[:-4]
    return t


#---------------------------------------------------------------------

def bsColumns(hs, numColumns, linSize='md'):
    """ Bootstrap multiple columns
    @param hs::[str] = each string contains html
    @param numColumns::int = number of columns. values are 2|3|4|6.
    @param linSize::str = linearize on size. Linearize means revert to a
        one-column setup when screen width gets below a certain size. Allowed
        values are:
       'xs' = never linearize
       'sm' = on <768 pixels
       'md' = on <992 pixels
       'lg' = on <1200 pixels
    @return::str containing html
    """
    if numColumns not in (2,3,4,6) or len(hs)<2*numColumns:
        h = ("""<div class='container-fluid'><div class='row'>
            <div class='col-md-12'>
            """
            + "<br>\n".join(hs)
            + "</div></div></div>\n")
        return h
    columnClass = "col-{}-{}".format(linSize, 12/numColumns)
    itemsPerRow = int(math.ceil(len(hs)*1.0 / numColumns))

    h = "<div class='container-fluid'><div class='row'>\n"
    for rowIx in range(numColumns):
        f = itemsPerRow * rowIx
        useHs = hs[f:f+itemsPerRow]
        h += form("""<div class='{columnClass}'>
{elements}
</div>
""",
            columnClass = columnClass,
            elements = "<br>\n".join(useHs))
    #//for row
    h += "</div></div>\n"
    return h



#---------------------------------------------------------------------

#end
