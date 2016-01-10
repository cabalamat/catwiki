# butil.py = low-level utilities

"""
History:

16-Sep-2014: added mystr() function

12-Feb-2015: added makeEmptyDir() function

28-Oct-2015: added attrEscape, attrUnescape function

"""

import os, os.path, stat, glob, fnmatch, shutil
import string, datetime, pprint

debug=False # debugging this module?

#---------------------------------------------------------------------

def isDir(s):
    try:
        s = os.path.expanduser(s)
        mode = os.stat(s)[stat.ST_MODE]
        result = stat.S_ISDIR(mode)
        return result
    except:
        return False


def entityExists(fn):
    """ Does a file-like entity (eg. file, symlink, directory) exist?
    @param fn [string] = a filename or pathname
    @return [boolean] = True if (fn) is the filename of an existing entity.
    """
    if debug: print "entityExists(%r)" % (fn,)
    fn = os.path.expanduser(fn)
    exists = os.access(fn, os.F_OK)
    return exists

def makeEmptyDir(dirPan):
    """ Cause dirPan to be an existing directory that is empty
    @param dirPan::str = pathname to directory
    """
    if entityExists(dirPan):
        if isDir(dirPan):
            shutil.rmtree(dirPan)
        else:
            os.remove(dirPan)
    os.makedirs(dirPan)


def fileExists(fn):
    """ Does a file exist?
    @param fn [string] = a filename or pathname
    @return [boolean] = True if (fn) is the filename of an existing file
    and it is readable.
    """
    if debug: print "fileExists(%r)" % (fn,)
    fn = os.path.expanduser(fn)
    readable = os.access(fn, os.R_OK)
    # (if it doesn't exist, it can't be readable, so don't bother
    # testing that separately)

    if not readable: return 0

    # now test if it's a file
    mode = os.stat(fn)[stat.ST_MODE]
    return stat.S_ISREG(mode)


def yy_getFilenames(dir, pattern):
    """ Return a list of all the filenames in a directory that match a
    pattern.
    **********************************************************
    NOTE (23-Jun-2004,PH): there are problems with glob.glob()
    which prevent this from working; use the alternate version
    below. I think this is a bug in Python 2.3.3.
    **********************************************************

    @param dir [string] a directory
    @param pattern [string] a Unix-style file wildcard pattern
    @return [list of string]
    """
    joined = os.path.join(dir, pattern)
    pathnames = glob.glob(joined)
    print "getFilenames(%r, %r) joined=%r pathnames=%r" % \
       (dir, pattern, joined, pathnames)
    filenames = [os.path.basename(pan) for pan in pathnames]
    filenames.sort()
    print "getFilenames(%r, %r) ==> %r" % (dir, pattern, filenames)
    return filenames

def getFilenames(dir, pattern="*"):
    """ Return a list of all the filenames in a directory that match a
    pattern. Note that this by default returns files and subdirectories.
    @param dir [string] a directory
    @param pattern [string] a Unix-style file wildcard pattern
    @return [list of string] = the files that matched, sorted in ascii
       order
    """
    #joined = os.path.join(dir, pattern)
    joined = os.path.join(normalisePath(dir), pattern)
    try:
        filenames = os.listdir(dir)
    except:
        filenames = []
    #print "xx_getFilenames(%r, %r) joined=%r filenames=%r" % \
    #   (dir, pattern, joined, filenames)
    matching = []
    for fn in filenames:
        if fnmatch.fnmatch(fn, pattern):
            matching.append(fn)
    #print "xx_getFilenames() matching=%r" % (matching,)
    matching.sort()
    return matching

def getMatchingSubdirs(d, pattern):
    files, dirs = getFilesDirs(d)
    matching = []
    for sd in dirs:
        if fnmatch.fnmatch(sd, pattern):
            matching.append(sd)
    matching.sort()
    return matching


def getFilesDirs(topDir):
    """ Return a list of all the subdirectories of a directory.
    @param dir [string]
    @return [list] = has two members (files, dirs) each of which
       are lists of strings. each member is the basename (i.e. the name
       under (topDir), not the full pathname)
    """
    filesAndDirs = os.listdir(topDir)
    files = []
    dirs = []
    for ford in filesAndDirs:
        fullPath = os.path.join(topDir, ford)
        if isDir(fullPath):
            dirs.append(ford)
        else:
            files.append(ford)
    files.sort()
    dirs.sort()
    return (files, dirs)


def normalizePath(p, *pathParts):
    """ Normalize a file path, by expanding the user name and getting
    the absolute path.
    @param p [string] = a path to a file or directory
    @param pathParts [list of string] = optional path parts
    @ return [string] = the same path, normalized
    """
    p1 = os.path.abspath(os.path.expanduser(p))
    if len(pathParts)>0:
        allPathParts = [ p1 ]
        allPathParts.extend(pathParts)
        p1 = os.path.join(*allPathParts)
    p2 = os.path.abspath(p1)
    return p2
normalisePath=normalizePath # alternate spelling
join=normalizePath # it works like os.path.join, but better

def getFileSize(pan):
    """ return the size of a file in bytes.
    @param pan [string] = a pathname
    @return [int]
    """
    try:
        size = os.stat(pan).st_size
    except:
        size = 0
    return size

def getFileAlterTime(pan):
    """ Get the time a file was last altered, as a datetime.datetime
    @param pan [string] = a pathname
    @return [datetime.datetime]
    """
    modified = os.stat(pan).st_mtime
    mDT = datetime.datetime.fromtimestamp(modified)
    return mDT

def _getCommonPrefixDir(pd1, pd2):
    """ Return the common prefix directory the arguments. Notre that this
    function doesn't inspect the filesystem. If (pd1) or (pd2) are directories
    they should end in "/". They should both be ablsolute, i.e. start with
    "/".
    @param pd1 [string] = path or directory
    @param pd2 [string] = path or directory
    @return [string]
    """
    cp = ""
    maxSame = 0
    while True:
        if len(pd1) <= maxSame: break
        if len(pd2) <= maxSame: break
        if pd1[maxSame] != pd2[maxSame]: break
        if pd1[maxSame] == "/":
            cp = pd1[:maxSame]
        maxSame += 1
    #//while
    return cp


def getRelativePath(toPan, fromDir):
    """ Return a relative path to a file, starting from a directory.
    @param toPan [string] = pathname of file to go to
    @param fromDir [string] = directory to come from
    @return [string]
    """
    #>>>>> expand ~
    if toPan[:1] == "~": toPan = os.path.expanduser(toPan)
    if fromDir[:1] == "~": fromDir = os.path.expanduser(fromDir)

    if fromDir == "" or fromDir == "/": return toPan

    if len(fromDir)>1 and fromDir[-1:] != "/":
        fromDir = fromDir + "/"

    common = _getCommonPrefixDir(toPan, fromDir)
    #print "common=%r" % (common,)
    if common == "" or common == "/": return toPan
    fromDirEnd = fromDir[len(common):]
    fromDirEndTimesGoBack = string.count(fromDirEnd, "/") - 1

    toEnd = toPan[len(common)+1:]
    result = ("../"*fromDirEndTimesGoBack) + toEnd
    return result

def deleteFile(pan):
    pan = normalizePath(pan)
    if fileExists(pan):
        os.remove(pan)


#---------------------------------------------------------------------
# read and write files:

def readFile(filename):
    pn = normalizePath(filename)
    f = open(pn, 'r')
    s = f.read()
    f.close()
    return s


def writeFile(filename, newValue):
    pn = normalizePath(filename)
    # create directories if they don't exist
    dirName = os.path.dirname(pn)
    if dirName:
        if not entityExists(dirName):
            os.makedirs(dirName)
    f = open(pn, 'w')
    f.write(newValue)
    f.close()


def readFileUtf8(filename):
    """ A file contains unicode text, encoded as utf-8.
    Save this into a unicode object.
    @param filename::str = pathname to file
    @return::unicode
    """
    pn = normalizePath(filename)
    f = open(pn, 'r')
    s = f.read()
    f.close()
    u = s.decode('utf8', 'ignore')
    return u
 

def writeFileUtf8(filename, newValue):
    """ write Unicode text to a file, using the utf-8 encoding
    @param filename::str = the pathname to the file
    @param newValue::unicode = the data to be written
    """
    pn = normalizePath(filename)

    # create directories if they don't exist
    dirName = os.path.dirname(pn)
    if dirName:
        if not entityExists(dirName):
            os.makedirs(dirName)
    f = open(pn, 'w')
    f.write(newValue.encode('utf8'))
    f.close()


def readPretty(filename):
    """ load data from a pretty-printed ascii file
    @param filename [string] = a filename or pathname
    """
    objectAsPretty = readFile(filename)
    return eval(objectAsPretty)

def writePretty(filename, object):
    """ save data as a pretty-printed ascii file
    @param filename [string] = a filename or pathname
    @param object = any Python object
    """
    pp = pprint.PrettyPrinter(indent=2)
    objectAsPretty = pp.pformat(object)
    writeFile(filename, objectAsPretty)

def pretty(ob, indent=4):
    pp = pprint.PrettyPrinter(indent)
    s = pp.pformat(ob)
    return s

#---------------------------------------------------------------------

def fromto(f, t):
    """ Return a list containing all the integers from (f) to (t),
    inclusive.
    @param f [int]
    @param t [int]
    @param step [int]
    @return [list]
    """
    return range(f, t+1)

def fromtostep(f, t, step):
    """ Return a list containing all the numbers from (f) to (t),
    inclusive, in steps of (step).
    @param f [number]
    @param t [number]
    @param step [number]
    @return [list]
    """
    result = []
    if step == 0: return result
    if step<0:
        direction = -1
    else:
        direction = 1
    value = f
    while value*direction <= t*direction:
        result.append(value)
        value += step
    return result


def resizeTuple(t, newSize, newValues=None):
    """ resize a tuple
    @param t::()
    @param newSize::int = the new size of the tuple
    @param newValues = what values to put in any new required elements
    """
    if len(t)==newSize:
        return t
    elif len(t)>newSize:
        return tuple(list(t)[:newSize])
    else:
        # tuple is too small
        a = list(t)
        numNew = newSize - len(a)
        a = a + [newValues]*numNew
        return tuple(a)


def unique(a):
    """ remove duplicates from a list.
    @param a::[] = an array of something (contents must be hashable)
    @return::[] = same as (a) but with duplicates removed
    """
    inserted = set()
    r = []
    for e in a:
        if e not in inserted:
            r.append(e)
            inserted.add(e)
    return r

#---------------------------------------------------------------------

def niceMe(newNice):
    """ renice the current process. """
    pid = os.getpid()
    os.system("renice %d -p %d" % (newNice, pid))

#---------------------------------------------------------------------

def getYN(question):
    """ Get a yes or no answer to a question, using the command line.
    @param question [string] = a question to ask the user
    @return [bool]
    """
    answer = raw_input(question + " (Y/N)?")
    isYes = string.upper(answer[:1]) == "Y"
    return isYes

def exValue(f, orValue):
    """ Evaluate function f. If it returns a value, return it.
    If it throws an exception, return (orValue) instead
    @param f::function
    @param orValue
    """
    r = orValue
    try:
        r = f()
    except:
        r = orValue
    return r

#---------------------------------------------------------------------

def items(arrOrDict):
    """ get key, value pairs for a list.
    ********************************************************
    Note: has been superceded by enumerate() function in
    standard library.
    ********************************************************
    @param arr [list|dict]
    @return [list of list [int,something]]
    """
    result = []
    if isinstance(arrOrDict, dict):
        d = arrOrDict
        keys = d.keys()
        keys.sort()
        for k in keys:
            item = (k, d[k])
            result.append(item)
    else:
        for ix in range(len(arrOrDict)):
            item = (ix, arrOrDict[ix])
            result.append(item)
    return result

def arrayGet(arr, ix, default):
    result = default
    try:
        result = arr[ix]
    except:
        pass
    return result

#---------------------------------------------------------------------
# string functions

def rFixSize(s, n):
    """ Return a string of size (n) chars, containing the text in (s).
    If (s) is bigger than (n) chars, cut off the right-hand end. If
    (s) is smaller than (n), move it to the right of the resultant string.
    @param s [string]
    @param n [int]
    @return [int]
    """
    s = s[:n]
    padNum = n - len(s)
    result = (" "*padNum) + s
    return result

def lFixSize(s, n):
    """ Return a string of size (n) chars, containing the text in (s).
    If (s) is bigger than (n) chars, cut off the right-hand end. If
    (s) is smaller than (n), move it to the left of the resultant string.
    @param s [string]
    @param n [int]
    @return [int]
    """
    s = s[:n]
    padNum = n - len(s)
    result = s + (" "*padNum)
    return result

def displayIntComma(i, useChar=',', dist=3):
    """ Return an int as a string with comma delimiters """
    if i < 0:
        resPlus = displayIntComma(-i)
        return "-" + resPlus
    s = "%d" % i
    ln = len(s)
    result = ""
    prev = 0
    for mark in fromtostep(ln%3, ln, dist):
        if mark > 0: result += s[prev:mark] + useChar
        prev = mark
    return result[:-1]

def getInt(s, notFoundReturn=-1):
    """ attempt to find a positive integer in a string
    @param s [string]
    @param notFoundReturn = value to be returned if no integer is found
    @return int
    """
    firstIx = -1
    for i, c in enumerate(s):
        if c in "0123456789":
            firstIx = i
            break

    if firstIx == -1:
        return notFoundReturn

    to = firstIx+1
    while 1:
        #print "s=%r firstIx=%r to=%r" % (s, firstIx, to)

        # if (nextIx) at end of string, break
        if to+1 > len(s): break
        ch = s[to]
        #print "to=%r ch=%r" % (to, ch)
        if ch not in "0123456789": break
        to += 1
    #print "firstIx=%r to=%r" % (firstIx, to)
    numStr = s[firstIx:to]
    return int(numStr)

def myStr(x):
    """ My version of the str() conversion function. This converts any
    type into a str. If x is a unicode, it is converted into a utf-8
    bytestream.
    @param x = a value of some type
    @return::str
    """
    if type(x)==unicode:
        return x.encode('utf-8')
    else:
        return str(x)
mystr = myStr

def form(s, *args, **kwargs):
    return s.format(*args, **kwargs)

def joinWith(separator, *args):
    """ Join each arg in args with separator, but only if they aren't
    empty.
    @param separator::str
    @param args::[str]
    @return str
    """
    r = ""
    first = True
    for arg in args:
        if arg != "":
            if not first:
                r += separator
            r += arg
        first = False
    #//for
    return r

def pcreEscape(s):
    """ Escapes a string for PCRE (Perl-Compatible Regular Expressions,
    see http://www.pcre.org/)
    @param s::str = a string containing the exact characters that are
        to be searched for
    @return::str = the equivalent string with PCRE special characters
        escaped with '\'.
    """
    PCRE_SPECIAL_CHARS = r"""?!+*{},^$'"`\():|<>#-=%"""
    r = ""
    for ch in s:
        if ch in PCRE_SPECIAL_CHARS:
            r += "\\" + ch
        else:
            r += ch
    #//for ch
    return r

#---------------------------------------------------------------------
# html attribute decoding

HTML_DECODE = [ ('&#39;', "'"),
                ('&quot;', '"'),
                ('&lt;', '<'),
                ('&gt;', '>'),
                ('&amp;', '&') ]
def attrEscape(s, noneIs=''):
    """ Escapes a string for html attribute special characters
    @param s::str = a string
    @return::str = the equivalent string with chanracters escaped
    """
    if s==None: return noneIs
    if not (isinstance(s, str) or isinstance(s,unicode)):
        s = myStr(s)
    hdc = HTML_DECODE[-1:] + HTML_DECODE[:-1]
    for encoded, decoded in hdc:
        s = s.replace(decoded, encoded)
    return s
attrEsc = attrEscape

def attrUnescape(s):
    """ opposite of attrEscape """
    for fromStr, toStr in HTML_DECODE:
        s = s.replace(fromStr, toStr)
    return s
attrUnEsc = attrUnesc = attrUnescape

#---------------------------------------------------------------------


class Struct:
    """ an anonymous object whose fields can be accessed using dot
    notation.
    See <http://norvig.com/python-iaq.html>
    """

    def __init__(self, **entries):
        self.__dict__.update(entries)

    def __repr__(self):
        keys = sorted(self.__dict__.keys())
        args = ["%s=%r" % (key, self.__dict__[key])
                for key in keys]
        return 'Struct(%s)' % ', '.join(args)

    def hasattr(self, key):
        return self.__dict__.has_key(key)

#---------------------------------------------------------------------

#end
