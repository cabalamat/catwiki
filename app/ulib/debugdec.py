# debugdec.py = decorators useful for debugging

"""
(c) 2013,2014 Philip Hunt, cabalamat@gmail.com
You may use this software under the terms of the MIT license. See file
<LICENSE> for details.
"""

import inspect
import datetime
import functools
import sys

# if you want to disable this module, set this to False eleswhere.
debugging = True

#---------------------------------------------------------------------

_PRINTARGS_DEPTH = 0
_PRINTARGS_INDENT = "| "

def printargs(fn):
    if not debugging:
        return fn
    @functools.wraps(fn)    
    def wrapper(*args, **kwargs):
        global _PRINTARGS_DEPTH
        argStr = ", ".join([repr(a) for a in args])
        kwargStr = ", ".join(["%s=%r"%(k,v) for v,k in enumerate(kwargs)])
        comma = ""
        if argStr and kwargStr: comma = ", "
        akStr = argStr + comma + kwargStr
        print '%s%s(%s)' % (_PRINTARGS_INDENT * _PRINTARGS_DEPTH,
           fn.__name__, akStr)
        _PRINTARGS_DEPTH += 1
        retVal = fn(*args, **kwargs)
        _PRINTARGS_DEPTH -= 1
        if retVal != None:
            print "%s%s(%s) => %r" % (_PRINTARGS_INDENT * _PRINTARGS_DEPTH,
               fn.__name__, akStr,
               retVal)
        return retVal
    return wrapper

#---------------------------------------------------------------------
"""
This decorator prints to stdout how long a function took to run.
"""

def timing(fn):
    if not debugging:
        return fn
    def wrapper(*args, **kwargs):
        before = datetime.datetime.now()
        retVal = fn(*args, **kwargs)
        after = datetime.datetime.now()
        elapsed = after - before
        ms = elapsed.total_seconds()*1000.0
        print "%s() took %.3f ms" % (fn.__name__, ms)
        return retVal
    return wrapper    

#---------------------------------------------------------------------
"""
Type checking works like this:

@typ(int, ret=int)
def foo(x):
    return x*x

"""

def typeName(ty):
    """ Return the name of a type, e.g.:
    typeName(int) => 'int'
    typeName(Foo) => 'Foo'
    typeName((int,str)) => 'int or str'
    @param ty [type|tuple of type]
    @return [str]
    """
    if isinstance(ty, tuple):
        return " or ".join(t.__name__ for t in ty)
    else:
        return ty.__name__

class typ:
    """ decorator to check a functions argument type """

    def __init__(self, *argTypes, **retType):
        self.argTypes = argTypes
        if retType.has_key('ret'):
            self.ret = retType['ret']
        else:    
            self.ret = None
        
        
    def __call__(self, fn):
        """ return a new function that when called, checks
        the arguments before calling the original function. 
        """
        if not debugging:
            return fn
        isMethod = inspect.getargspec(fn).args[0] == 'self'     
        @functools.wraps(fn)  
        def wrapper(*args):
            if isMethod:
                checkArgs = args[1:]
            else:    
                checkArgs = args
            # check number of args
            if len(checkArgs)<len(self.argTypes):
                msg = ("%s() called with too few args (%d), should be >=%d"
                    % (fn.__name__, len(checkArgs), len(self.argTypes)))
                raise TypeError(msg)
            # check args
            for ix, arg in enumerate(checkArgs):
                sbType = self.argTypes[ix] # what the type should be
                if sbType!=None and not isinstance(arg, sbType):
                    msg = ("calling %s(), arg[%d] had type of %s,"
                        " should be %s") % (fn.__name__, 
                        ix, 
                        type(arg).__name__,
                        typeName(sbType))
                    raise TypeError(msg)
            retval = fn(*args)
            # check return type
            if self.ret!=None and not isinstance(retval, self.ret):
                msg = ("%s() returns type of %s,"
                        " should be %s") % (fn.__name__, 
                        type(retval).__name__,
                        typeName(self.ret))
                raise TypeError(msg)
            return retval
        return wrapper  


#---------------------------------------------------------------------
# print values

def _prVarsSelf(cLocals, vn):
    selfOb = cLocals['self']
    value = selfOb.__dict__[vn[5:]]
    r = " %s=%r" % (vn, value)
    return r

def prvars(varNames =None):
    if not debugging: return  
    if isinstance(varNames, str):
       vnList = varNames.split()   
    caller = inspect.stack()[1]
    cLocals = caller[0].f_locals # local variables of caller
    #print cLocals
    fileLine = caller[2]
    functionName = caller[3]
    filename = caller[0].f_code.co_filename
    output = "%s():%d" % (functionName, fileLine)
    outputForSelf = " "*len(output)
    printAllSelf = False
    if varNames==None:
        for vn in sorted(cLocals.keys()):
            output += " %s=%r" %(vn, cLocals[vn])
        if cLocals.has_key('self'): printAllSelf = True
    else:    
        for vn in vnList:
            if vn.startswith("self."):
               output += _prVarsSelf(cLocals, vn)     
            elif cLocals.has_key(vn):
               output += " %s=%r" %(vn, cLocals[vn]) 
               if vn=='self': printAllSelf = True
    if printAllSelf:
        selfOb = cLocals['self']
        for insVar in sorted(selfOb.__dict__.keys()):
           val = selfOb.__dict__[insVar]
           output += "\n" + outputForSelf + " self.%s=%r"%(insVar,val)
    sys.stderr.write(output + "\n")
   
#---------------------------------------------------------------------
 
def pr(formatStr, *args):
    caller = inspect.stack()[1]
    cLocals = caller[0].f_locals # local variables of caller
    fileLine = caller[2]
    functionName = caller[3]

    if len(args)>0:
        s = formatStr % args
    else:
        s = formatStr
    t = "%s():%d: " % (functionName, fileLine)
    sys.stderr.write(t + s + "\n")

def prNo(formatStr, *args):
    """ as pr() but with no line numbers prepended """
    if len(args)>0:
        s = formatStr % args
    else:
        s = formatStr
    sys.stderr.write(s + "\n")

#---------------------------------------------------------------------

def getCallerLocals():
    """
    Get the local variables for the function that called the function
    that called this function (i.e. two call stack levels back)
    @return [dict]
    """
    caller2 = inspect.stack()[2]
    return caller2[0].f_locals
    
def getCallerLocal(varName):
    """
    Get a local variable for the function that called the function
    that called this function (i.e. two call stack levels back)
    @param varName [str] the name of the variable we want
    @return [dict]
    """
    caller2 = inspect.stack()[2]
    return caller2[0].f_locals[varName]
    

#---------------------------------------------------------------------


#end
