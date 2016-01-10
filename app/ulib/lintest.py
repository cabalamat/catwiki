# lintest.py = linear regression testing

"""***
linear testing framework

Last altered: 20-Jan-2014

History:
6-May-2004: created

4-Sep-2008: added new test:
FileAssertionMixin:assertFileDoesNotExist(pathname)

17-Feb-2011: copied back to pylib.

31-Jul-2013: added new assertion: assertDirExists(), to check
whether a directory exists.

31-Jul-2013: added 'require' facility so a TestCase can require other 
TestCases to be run before it. This is tested in <test_require.py>.

16-Jan-2014 added assertApprox for approximate comparisons of f.p. 
numbers

***"""

import sys, os.path, stat

import butil, termcolours
tc = termcolours.TermColours


#---------------------------------------------------------------------
# globals

debug = False

assertionsPassed = 0
functionsPassed = 0
testCasesRun = []

#---------------------------------------------------------------------

class ColoursMixin:
    PASSED = tc.GREEN + "PASSED" + tc.NORMAL
    FAILED = tc.RED + "FAILED" + tc.NORMAL
    
    # colours for a line noting entry into a test method
    TEST_METHOD_LINE = tc.BLUE
    NORMAL = tc.NORMAL

#---------------------------------------------------------------------

"""***
Abstract superclass for tests

Interface:
----------

Test instances should understand:
   run() - run all the tests in the test, and print results
***"""

class Test(object):

    def __init__(self, name =""):
        self.name = name
        self.tests = []
        self.parent = None

    def getFullName(self):
        fullName = self.getParentName()
        if len(fullName) > 0:
            fullName += " >> "
        fullName += self.name
        return fullName

    def getParentName(self):
        if self.parent:
            return self.parent.getFullName()
        else:
            return ""

    def printTestResults(self):
        p = "Passed %d assertions in %d test functions" \
           % (assertionsPassed, functionsPassed)
        ptop = "*" * (len(p)+6)
        ptop = tc.GREEN + ptop + tc.NORMAL
        s2 = tc.GREEN + "**" + tc.NORMAL
        print "\n%s\n%s %s %s\n%s" % (
            ptop,
            s2, p, s2,
            ptop)

#---------------------------------------------------------------------
"""***
A mixin that adds some assertions relating to files
***"""

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
    mode = os.stat(fn).st_mode
    return stat.S_ISREG(mode)

def dirExists(fn):
    """ Does a directory exist?
    @param fn [string] = a filename or pathname for a directory
    @return [boolean] = True if (fn) is the name of an existing directory
    and it is readable.
    """
    if debug: print "fileExists(%r)" % (fn,)
    fn = os.path.expanduser(fn)
    readable = os.access(fn, os.R_OK)
    # (if it doesn't exist, it can't be readable, so don't bother
    # testing that separately)
    if not readable: return 0
    # now test if it's a directory
    mode = os.stat(fn).st_mode
    return stat.S_ISDIR(mode)

class FileAssertionMixin(ColoursMixin):

    def assertFileExists(self, pan, comment=""):
        """ does file (pan) exist?
        @param pan [string] = a full pathname to a file
        """
        ok = fileExists(pan)
        if ok:
            self.passedTest("%s; file <%s> exists" % (comment, pan))
        else:
            msg = "FAILED: %s; file <%s> doesn't exist" % (comment, pan)
            raise AssertionError, msg

    def assertFileDoesNotExist(self, pan, comment=""):
        """ does file (pan) exist? It shouldn't.
        @param pan [string] = a full pathname to a file
        """
        ok = not fileExists(pan)
        if ok:
            self.passedTest("%s; file <%s> correctly doesn't exist"\
               % (comment, pan))
        else:
            msg = "FAILED: %s; file <%s> exists, when it shouldn't"\
               % (comment, pan)
            raise AssertionError, msg

    def assertDirExists(self, pan, comment=""):
        """ does directory (pan) exist?
        @param pan [string] = a full pathname to a file
        """
        ok = dirExists(pan)
        if ok:
            self.passedTest("%s; directory <%s> exists" % (comment, pan))
        else:
            msg = "FAILED: %s; directory <%s> doesn't exist" % (comment, pan)
            raise AssertionError, msg

    def assertFilesEqual(self, pan1, pan2, comment=""):
        """ Do two files contain the same data?

        (maybe we should use diff for long files?)

        @param pan1 [string] = filename or pathname for 1st file
        @param pan2 [string] = filename or pathname for 2nd file
        @param comment [string]
        """
        data1 = butil.readFile(pan1)
        data2 = butil.readFile(pan2)
        if data1 == data2:
            self.passedTest("%s; files <%s> and <%s> contain the same data"
               % (comment, pan1, pan2))
        else:
            msg = "FAILED: %s; files <%s>, <%s> contain different data"\
               % (comment, pan1, pan2)
            raise AssertionError, msg

    def assertFileHasData(self, pan, data, comment=""):
        """ Are the contents of file (pan) equal to (data)?
        @param pan [string] = a full pathname to a file
        @param data [string] = what is supposed to be in the file
        """
        dataInFile = butil.readFile(pan)
        difDisplay = "%r" % (dataInFile,)
        if len(dataInFile) > 80:
            difDisplay = "%d chars starting with %r" \
               % (len(dataInFile), dataInFile[:80])

        if dataInFile == data:
            self.passedTest("%s; file <%s> has data: %s"
               % (comment, pan, difDisplay))
        else:
            dataDisplay = "%r" % (data,)
            if len(data) > 80:
                dataDisplay = "%d chars starting with %r" \
                   % (len(data), data[:80])
            msg = "FAILED: %s; file <%s> contains: %s\nshould be: %s"\
               % (comment, pan, difDisplay, dataDisplay)
            raise AssertionError, msg

    #========================================================
    # utility function:
    #========================================================

    def cmd(self, command):
        """ not a file assertion, but comes in incredibly useful """
        print "CMD { %s }" % command
        os.system(command)

#---------------------------------------------------------------------

"""***
Superclass for the user's test cases

***"""

class TestCase(Test, FileAssertionMixin, ColoursMixin):

    def passedTest(self, msg):
        global assertionsPassed
        assertionsPassed += 1
        print "%s - %s (%d)" % (msg, self.PASSED, assertionsPassed)

    #========================================================
    # assertions
    #========================================================

    def assertEqual(self, r, sb, comment=""):
        com2 = ""
        if comment:
            com2 = comment + "; "
        ok = (r == sb)
        if ok:
            msg = "%sr=%r" % (com2, r)
            self.passedTest(msg)
        else:
            msg = "FAILED: %sassertEqual\nr = %r\nsb= %r" % (com2, r, sb)
            raise AssertionError, msg
    assertSame = assertEqual
    
    def assertApprox(self, r, sb, comment=""):
        com2 = ""
        if comment:
            com2 = comment + "; "
        epsilon = 0.0001
        bigger = 1 + epsilon
        smaller = 1 - epsilon
        ok = (r == sb
              or sb*smaller < r < sb*bigger
              or sb*smaller > r > sb*bigger
        )
        if ok:
            msg = "%sr=%r" % (com2, r)
            self.passedTest(msg)
        else:
            msg = "FAILED: %sassertApprox\nr = %r\nsb= %r" % (com2, r, sb)
            raise AssertionError, msg

    def assertNotEqual(self, r, snb, comment=""):
        com2 = ""
        if comment:
            com2 = comment + "; "
        ok = (r != snb)
        if ok:
            msg = "%sr=%r r!=%r" % (com2, r, snb)
            self.passedTest(msg)
        else:
            msg = "FAILED: %sassertNotEqual\nr=%r\n(should be different)"\
               % (com2, r)
            raise AssertionError, msg

    def assertBool(self, bool, comment=""):
        if bool:
            self.passedTest("%s; true" % comment)
        else:
            raise AssertionError, "Failed: %s" % comment
    assertTrue = assertBool
    assert_ = assertBool
    failUnless = assertBool

    def assertFalse(self, bool, comment=""):
        if not bool:
            self.passedTest("%s; correctly false" % comment)
        else:
            raise AssertionError, "Failed: %s" % comment
    failIf = assertFalse

    def failed(self, comment=""):
        # failed a test
        raise AssertionError, "Failed: %s" % comment
    fail = failed

    def passed(self, comment=""):
        # passed a test
        self.passedTest("%s; passed" % comment)

    #========================================================

    #def setUpAll(self): pass
    #def setUp(self): pass
    #def tearDown(self): pass
    #def tearDownAll(self): pass

    #========================================================
    # running tests
    #========================================================

    def run(self, parent =None):
        global functionsPassed, testCasesRun
        self.optCR = "\n"
        if parent: self.parent = parent 
        self._runRequirements(parent)
        testCasesRun.append(self.__class__)

        #self.parent = parent
        kn = self.__class__.__name__
        tests = self.getTests()

        self.doRun("setUpAll")
        for test in tests:
            self.doRun("setUp")
            kn = self.__class__.__name__
            funName = test.func_code.co_name
            funLineNum = test.func_code.co_firstlineno
            print "%s%s=== %s%s.%s:%d ===%s" \
                % (self.optCR, 
                   self.TEST_METHOD_LINE,
                   self._pnTxt(), kn, funName,
                   funLineNum,
                   self.NORMAL)
            test(self)
            functionsPassed += 1
            self.doRun("tearDown")
            self.optCR = "\n"
        self.doRun("tearDownAll")
        if not self.parent:
            self.printTestResults()           

    def _pnTxt(self):
        pn = self.getParentName()
        if len(pn)>0: pn += " >> "
        return pn

    def canRun(self, methodName):
        b = hasattr(self, methodName)
        return b

    def doRun(self, methodName):
        if self.canRun(methodName):
            print "%s%s@@@ %s.%s()%s" % (
                self.optCR,
                self.TEST_METHOD_LINE,
                self.__class__.__name__, methodName,
                self.NORMAL)
            exec("self.%s()" % methodName)
            self.optCR = ""

    def getTests(self):
        """ Return all the test functions in this class """
        if debug: print "getTests() dict=%r" % self.__class__.__dict__

        tests = []
        for k,v in self.__class__.__dict__.items():
            if k[:5] == "test_":
                vfc = v.func_code
                #print "test function: %s (%d)" % (vfc.co_name, vfc.co_firstlineno)
                tests.append(v)
        tests.sort(compare_funs)
        if debug: print "getTests() => %r" % (tests,)
        return tests
        
    #=======================================================
    # running requirements
    #=======================================================    

    def _runRequirements(self, parent):
        """ Does this TestCase need any other test cases to be run 
        before it can be run? If so, run them
        """
        global testCasesRun
        reqs = self._getRequirements()
        #print "_runRequirements() reqs=%r" % (reqs,)
        for req in reqs:
            if req not in testCasesRun:
                print "%s requires %s, running it first..."\
                    % (self.__class__.__name__, req.__name__)
                reqInstance = req()
                self.name = "(%s)" % self.__class__.__name__
                reqInstance.run(self)
        #//for        
            
    def _getRequirements(self):
        """ get the requirements of this TestCase,
        which are stored in the requires class variable.
        If it isn't a list, make it one.
        @return [list of TestCase]
        """
        try:
            r = self.requires
        except:
            r = []
        if isinstance(r, tuple):  
            r = list(r)
        elif not isinstance(r, list):
            r = [r]
        return r    
        
        
#---------------------------------------------------------------------
# comparison function for functions

def compare_funs(f1, f2):
    f1c = getFunCollate(f1)
    f2c = getFunCollate(f2)
    result = cmp(f1c, f2c)
    return result

def getFunCollate(f):
    ffc = f.func_code
    r = "%05d %s" % (ffc.co_firstlineno, ffc.co_name)
    return r

#---------------------------------------------------------------------

"""***
A group of TestCases (or TestGroups)

Interface:
----------

TestGroup

addCase(TestCaseSubclass)
addTest(aTestGroup)
add(aModule) - do later?
add(list of these)

***"""

class TestGroup(Test):

    def __init__(self, name =None):
        Test.__init__(self, name)
        self.name = name
        self.tests = []
        self.parent = None

        if self.name == None:
            # use defualt value for name, which is the filenamer of the
            # calling module
            frame = sys._getframe(1)
            fn = frame.f_code.co_filename
            shortFn = os.path.basename(fn)
            root, extension = os.path.splitext(shortFn)
            self.name = root
            if debug: print "TestGroup is taking name %r" % self.name

    #========================================================
    # running tests
    #========================================================

    def run(self, parent =None):
        self.parent = parent
        for test in self.tests:
            test.run(self)
        if not self.parent:
            self.printTestResults()

    #========================================================
    # adding tests
    #========================================================

    def addTest(self, aTest):
        """add a test to the group.
        @param aTest [Test]
        """
        self.tests.append(aTest)


    def addCase(self, testCaseSubclass):
        """ add a subclass of TestCase to the group.
        @param testCaseSubclass [class]
        """
        if debug: print "... adding test case %s" % testCaseSubclass.__name__
        inst = testCaseSubclass()
        self.addTest(inst)

    def add(self, *args):
        """ add some Tests of TestCase subclasses to this group """
        for arg in args:
            if isinstance(arg, Test):
                self.addTest(arg)
            else:
                self.addCase(arg)


#---------------------------------------------------------------------

#end
