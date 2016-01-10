# istream.py

"""
input streams for Python

History:
16-Dec-2006: implemented PeekStream:peekStr()

10-Apr-2007: added IStream:grabToString()

2-May-2007: added IStream:grabToBefore()

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
Class hierarchy;

IStream (ab)
   IFile -- a readable file
   PeekStream (ab)
      ScanString -- a scannable string
      FileWrapper

"""

import string

debug = False # debugging this module?

#---------------------------------------------------------------------

DIGITS = "0123456789"
LETTERSU = string.ascii_letters + "_"
IDENTCHARS = LETTERSU + string.digits

def cin(c, s):
    """ is c in s? If c is empty, return False.
    @param c [string] = a character or ''
    @param s [string] = a string; c must match one char in s
    @return [bool]
    """
    if c=='': return False
    return c in s

def isDigit(c):
    return cin(c, DIGITS)

def isLetterU(c):
    return cin(c, LETTERSU)

def isIdentChar(c):
    return cin(c, IDENTCHARS)

#---------------------------------------------------------------------

class IStream:

    #========================================================
    # to be implemented by subclasses:

    def get(self):
        """ Get the next character in the stream
        @return [string] length 1; or '' if EOF
        """
        raise NotImplementedError

    def eof(self):
        """ are we at the end of this stream?
        @return [bool]
        """
        raise NotImplementedError

    #========================================================

    def getChar(self):
        """ alias for get() """
        return self.get()

    def getLine(self):
        """ Get the next line, including '\n' at end
        @return [string]
        """
        if debug:
            print "*** in getLine() ***"
        line = ""
        while 1:
            nextChar = self.get()
            if debug:
                print "*** in getLine() 2. nextChar=%r ***" % (nextChar,)
            if nextChar == "": return line
            if debug:
                print "*** in getLine() 3. nextChar=%r ***" % (nextChar,)
            line += nextChar
            if nextChar == "\n": return line

    def getLines(self):
        """ Get all the lines
        @return [list of string]
        """
        lines = []
        while 1:
            line = self.getLine()
            if line == "": return lines
            lines += [line]

    def getAll(self):
        """ Get all the characters in the stream as a string
        @return [string]
        """
        lines = self.getLines()
        return string.join(lines, "")

    def getChars(self, n =-1):
        """ Get (n) characters in the stream. If n<0, get the lot.
        @return [string]
        """


#---------------------------------------------------------------------
"""
A wrapper round a file object

Instance variables
~~~~~~~~~~~~~~~~~~
atEnd [bool] are we at the end of the file?
f [file] the underlying file object
"""

class IFile(IStream):

    def __init__(self, file= None, filename= None):
        """
        Create a new IFile. Either file or filename must be set.
        @param file [file] = a file object
        @param filename = a filename or pathname
        """
        if file:
            self.f = file
        elif filename:
            pass
        else:
            msg = "Error in creating IFile; must include file or"\
               " filename (file=%r, filename=%r)" % (file, filename)
            raise Exception(msg)
        self.atEnd = False

    def get(self):
        ch = self.f.read(1)
        if len(ch)==0: self.atEnd = True
        return ch

    def eof(self):
        return self.atEnd


#---------------------------------------------------------------------

class PeekStream(IStream):

    #========================================================
    # to be implemented by subclasses:

    def peek(self, lookahead=0):
        """ Returns a peek of one char. If lookahead==0, returns the
        next to be written in the stream.
        @param n [int]
        @return [string] length 1; or "" if no more chars
           at relevant position
        """
        raise NotImplementedError

    #========================================================

    def eof(self):
        return self.peekChar()==''

    def peekChar(self, lookahead=0):
        """ alias for peek() """
        return self.peek(lookahead)

    def yyypeekStr(self, n, lookahead=0):
        """ peekStr(n) returns a peek of the next (n) chars; however
        peekStr(n, f) returns a peek of the next (n) characters,
           starting from an offset of (f) characters ahead from the
           current position.
        @param n [int]
        @param lookahead [int] = where to start looking from
        @return [string] length n or shorter if no more characters
        """

    def isNext(self, matchStr):
        """ Are the next chars are (matchStr)?
        @param matchStr [string]
        @return [bool]
        """
        return self.peekStr(len(matchStr)) == matchStr

    def isNextWord(self):
        """ Is what follows a C-style identifier?
        @return [bool]
        """
        ch = self.peek()
        return isLetterU(ch)

    def grabWord(self):
        """ grab a C-style identifier. Throw away characters until
        we're at the start of one, then greedily grab all of it.
        @return [string] = the identifier, or '' if couldn't get one
        """
        while 1:
            if self.peek()=='': return ''
            if self.isNextWord(): break
            self.get()
        r = ''
        r = self.get()
        while isIdentChar(self.peek()):
            r += self.get()
        return r

    def isNextInt(self):
        """ Is what follows an integer? (ie optional '-'
        followed by 1 or more [0-9]
        @return [bool]
        """
        c = self.peek()
        if c=='': return False
        if isDigit(c): return True
        if c=="-" and isDigit(self.peek(1)): return True
        return False

    def grabInt(self, notFound=None):
        """ Scan forward until an int is found, then return it.
        If no int found, return (notFound)
        @return [int]
        """
        while not self.isNextInt():
            c = self.get()
            if c == '': return notFound
        r = self.get()
        while isDigit(self.peek()):
            r += self.get()
        return int(r)


    def isNextSkip(self, matchStr):
        """ Are the next chars are (matchStr)? If so, skip them
        and return True.
        @param matchStr [string]
        @return [bool]
        """
        lm = len(matchStr)
        isNext = (self.peekStr(lm) == matchStr)
        if isNext: self.getChars(lm)
        return isNext

    def skipPast(self, s):
        """ Keep consuming characters until the most recently
        consumed are the string (s)
        @param s [string]
        @return [bool] True if skipped any characters
        """
        ls = len(s)
        if ls==0: return False
        while 1:
            if self.isNextSkip(s) or self.eof(): return True
            self.get()

    def grabToString(self, s):
        """ Keep reading characters until we either reach the end of
        the stream, or the most-recently-read characters are the string (s).
        If (s) is '', don't read any characters.
        Return all the characters read, including the (s) at the end.
        @param s [string]
        @return [string] = all the characters that have been grabbed
        """
        if s=="": return ""
        charsRead = ""
        lens = len(s)
        while 1:
            if self.eof(): return charsRead
            charsRead += self.get()
            if len(charsRead)>= lens and charsRead[-lens:]==s:
                # we've just read (s), so quit
                return charsRead
        #//while

    def grabToBefore(self, s):
        """ Keep reading characters until we either reach the end of
        the stream, or the next-to-be-read characters are the string (s).
        Return the characters grabbed. If what's next in the stream is
        (s), return an empty string.
        @param s [string] = a string which must follow the characters
           to be grabbed
        @return [string] = the characters grabbed
        """
        grabbed = ""
        while 1:
            if self.isNext(s): return grabbed
            if self.eof(): return grabbed
            grabbed += self.get()

    def isNextSkip_emptyLine(self):
        """ Are the next characters an empty line?
        If so, skip them and return True. If not, return False.
        An "empty line" means "\n\n".
        @return [bool]
        """
        return self.isNextSkip("\n\n")

    def skipPastSet(self, chars):
        """ Keep consuming characters until the next char to be read
        isn't in the set (chars),
        skip past it.
        @param chars [string]
        @return [bool] True if skipped any characters
        """
        r = False
        while 1:
            ch = self.peek()
            if ch=='': break
            if ch not in chars: break
            self.get()
            r = True
        return r


#---------------------------------------------------------------------

class ScanString(PeekStream):

    def __init__(self, s):
        """ create a scannable string
        @param s [string]
        """
        if debug and type(s)!=str:
            print "ScanString:__init__(%r) ***NOT A STRING***" % (s,)
            assert type(s)==str
        self.s = s
        self.at = 0

    #========================================================
    # inherited from superclasses:

    def get(self):
        ch = self.s[self.at:self.at+1]
        self.at += 1
        return ch

    def getChars(self, n=-1):
        if n<0:
            r = self.s[self.at:]
            self.at = len(self.s)
        else:
            ixto = self.at + n
            r = self.s[self.at:ixto]
            self.at += n
            if self.at > len(self.s): self.at = len(self.s)
        return r

    def peek(self, lookahead=0):
        ix = self.at + lookahead
        result = self.s[ix:ix+1]
        if debug:
            print "ScanString:peek(%r) ix=%r result=%r"\
               % (lookahead, ix, result)
        return result

    def peekStr(self, n, lookahead=0):
        """ peekStr(n) returns a peek of the next (n) chars; however
        peekStr(n, f) returns a peek of the next (n) characters,
           starting from an offset of (f) characters ahead from the
           current position.
        @param n [int]
        @param lookahead [int] = where to start looking from
        @return [string] length n or shorter if no more characters
        """
        ixto = lookahead + self.at + n
        return self.s[lookahead + self.at : ixto]

    #========================================================

#---------------------------------------------------------------------
"""
A wrapper around a file object (i.e. an object created with the Python
built-in file() function)

"""

class FileWrapper(PeekStream):
    def __init__(self, file= None, filename= None):
        """
        @param file [file] = a file object
        @param filename = a filename or pathname
        """
        if file:
            self.f = file
        elif filename:
            pass
        else:
            msg = "Error in creating FileWrapper; must include file or"\
               " filename (file=%r, filename=%r)" % (file, filename)
            raise Exception(msg)


    #========================================================
    # inherited from superclasses


    def get(self):
        """ return the next character
        return [string]
        """



    #========================================================

#---------------------------------------------------------------------


#end
