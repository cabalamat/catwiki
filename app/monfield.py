# monfield.py = fields for mongoab
# coding: utf-8

import re
import cgi
from xml.sax import saxutils

from bson.objectid import ObjectId

from ulib.debugdec import *

#---------------------------------------------------------------------
# helper stuff

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

class Incrementor:
    """ every time you call an instance of this class, it returns 1
    more than the last time it was called.
    """

    def __init__(self, before=0):
        self.i = before

    def __call__(self):
        self.i += 1
        return self.i

fieldIndex = Incrementor()

def pretty(ob):
    """ returns a string containing a pretty-printed representation of
    (ob).
    """
    import pprint, StringIO
    sio = StringIO.StringIO()
    pp = pprint.PrettyPrinter(indent=2, stream=sio)
    pp.pprint(ob)
    output = sio.getvalue()
    return output

def form(s, *args, **kwargs):
    return s.format(*args, **kwargs)

def titleize(fn):
    """ Convert a field name into a title
    @param fn [str] a field name
    @return [str]
    """
    fn = fn[:1].capitalize() + fn[1:]
    r = ""
    insideNumber = False
    for ch in fn:
        if ch.isupper() or (ch.isdigit() != insideNumber):
            r += " "
        r += ch
        insideNumber = ch.isdigit()
    return r.strip()

#---------------------------------------------------------------------
""" FieldInfo is the superclass for all the field classes

instance variables
~~~~~~~~~~~~~~~~~~
index [int] = a number increamented for each field created. Used to
    determine field order in a form.

desc [str] = a long description (about a line long) for the field

fieldName [str] = the name that the field is known as in the
    database. this is also used in html forms, etc.

title [str] = if used, this is the name of the field in a form. If not
    used, a title based on the fieldName is created

defaultValue = the default value for the data in this field

Constructors
~~~~~~~~~~~~
Constructors for fields take the following parameters:

desc [str] = a long description (about a line long) for the

default = sets the default value

null [bool] = can be null (only applies to key fields)
"""

class FieldInfo(object):
    """ superclass for MongoAb fields """

    def __init__(self, fieldName=None, **kwargs):
        self.index = fieldIndex()
        self.desc = ""
        self.readArgs(**kwargs)
        #print ("(%r) create %s, fieldName=%r kwargs=%r"
        #       % (self.index, self.__class__, fieldName, kwargs))

    def __repr__(self):
        r = "<%s %s>" % (self.__class__.__name__, self.fieldName)
        return r

    def createWithInitialValue(self):
        return self.defaultValue

    def readArgs(self, **kwargs):
        #print "FieldInfo:readArgs kwargs=%r" % (kwargs,)
        if kwargs.has_key("default"):
            self.defaultValue = kwargs['default']
        else:
            self.defaultValue = self.defaultDefault()
        if kwargs.has_key('desc'):
            self.desc = kwargs['desc']
        if kwargs.has_key('title'):
            self.title = kwargs['title']
        self.displayInForm = kwargs.get('displayInForm', True)
        self.fieldLen = kwargs.get('fieldLen', 20)
        self.formatStr = kwargs.get("formatStr", "{}")
        self.validateF = kwargs.get('validateF', None)

    def defaultDefault(self):
        """ return the default value for the default value of the
        object.
        """
        return None

    def isValidValue(self, v):
        """ Is (v) a valid value to go into this field?
        Defaults to True, will normally be over-ridden by subclass
        """
        return True

    def convertValue(self, v):
        """ Convert (v) into a value that is valid for this field,
        and return it.
        If it can't be converted, raise a ValueError.
        @param v [str]
        """
        return v

    def getOb(self, v):
        """ get an object from the database relating to this value.
        This method is overloaded by KeyField.
        """
        return v

    #========== html forms

    def formField(self, v):
        """ return  html for a form field for this fieldInfo """
        #if not self.displayInForm: return ""
        h = form('''<input class=gin id="id_{fieldName}" name="{fieldName}"
            type="text" value={v} size={fieldLen}>''',
            fieldName = self.fieldName,
            v = saxutils.quoteattr(self.formatStr.format(v)),
            fieldLen = self.fieldLen,
        )
        return h

    def readOnlyField(self, v):
        h = "<span class='read-only'>{}</span>".format(
            cgi.escape(self.formatStr.format(v)))
        return h

    @printargs
    def formLine2(self, v, **kwargs):
        """ new version (8-May-2014) of formLine() and
        formLineWithErrors().
        @param v = data in document for fieldName
        @param kwargs [dict]
        Arguments in kwargs are:
        - readOnly [bool], defaults to False. Make the form read-only.
        - withErrors [bool], defaults to False. If true, check for
          errors in the user's input and display them in the form.
        @return [str] containing HTML
        """
        if not self.displayInForm: return ""
        readOnly = kwargs.get('readOnly', False)
        withErrors = kwargs.get('withErrors', False)
        tooltip = ""
        if self.desc:
            tooltip = " title=%s" % saxutils.quoteattr(self.desc)

        if readOnly:
            formField = self.readOnlyField(v)
        else:
            formField = self.formField(v)

        errMsg = ""
        if withErrors: errMsg = self.errorMsg(v)
        errorInfo = ""
        formErrorLine = ""
        if errMsg:
            errorInfo = ("<br><div class='form-error'>"
                "<i class='fa fa-exclamation-triangle fa-lg'></i> "
                "{}</div>\n").format(
                cgi.escape(errMsg)
            )
            formErrorLine = " class='form-error-line'"
        h = form("""<tr {formErrorLine}>
                 <th><label for="id_{fieldName}"{tooltip}
                 >{title}</label></th>
                 <td>{formField} {errorInfo}</td>
                 </tr>""",
            formErrorLine = formErrorLine,
            fieldName = self.fieldName,
            tooltip = tooltip,
            title = self.getTitle(),
            formField = formField,
            #roc = " class='read-only'" if readOnly else "",
            errorInfo = errorInfo,
        )
        return h


    def formLine(self, v, readOnly=False):
        if not self.displayInForm: return ""
        tooltip = ""
        if self.desc:
            tooltip = " title=%s" % saxutils.quoteattr(self.desc)
        if readOnly:
            h = form("""<tr>
  <th>{title}</th>
  <td class='read-only'>{formField}</td>
</tr>""",
                fieldName = self.fieldName,
                title = self.getTitle(),
                formField = self.readOnlyField(v)
            )
        else:
            h = form("""<tr>
  <th><label for="id_{fieldName}"{tooltip}>{title}</label></th>
  <td>{formField}</td>
</tr>""",
                fieldName = self.fieldName,
                tooltip = tooltip,
                title = self.getTitle(),
                formField = self.formField(v)
            )
        return h

    def formLineWithErrors(self, v, formDataItem):
        if not self.displayInForm: return ""
        tooltip = ""
        if self.desc:
            tooltip = " title=%s" % saxutils.quoteattr(self.desc)
        errMsg = self.errorMsg(formDataItem)
        if errMsg:
            errorInfo = ("<br><div class='form-error'>"
                "<i class='fa fa-exclamation-triangle fa-lg'></i> "
                "{}</div>\n").format(
                cgi.escape(errMsg)
            )
            formErrorLine = " class='form-error-line'"
        else:
            errorInfo = ""
            formErrorLine = ""
        h = form("""<tr {formErrorLine}>
  <th><label for="id_{fieldName}"{tooltip}>{title}:</label></th>
  <td>{formField} {errorInfo}
  </td>
</tr>""",
            formErrorLine = formErrorLine,
            fieldName = self.fieldName,
            tooltip = tooltip,
            title = self.getTitle(),
            formField = self.formField(v),
            errorInfo = errorInfo,
        )
        return h

    def errorMsg(self, fs):
        """ Return an error message for the field info.
        This version of the method always returns ""; field types that
        can have errors will want to override this method.

        @param fs [str] the field in the form http POST request for
            this field.
        @return [str] If there is no error, this will be "".
            If there are any errors, this will be a helpful error
            message, which will be inserted in the form under the
            form field.
        """
        return self.callValidateF(fs)

    def callValidateF(self, fs):
        if self.validateF != None:
            result = self.validateF(fs, self)
            return result
        return ""


    #========== helper functions (default values for names)

    def getTitle(self):
        if hasattr(self, 'title'): return self.title
        self.title = titleize(self.fieldName)
        return self.title

#---------------------------------------------------------------------

class StrField(FieldInfo):
    """ a field holding a Python str """

    def readArgs(self, **kwargs):
        super(StrField, self).readArgs(**kwargs)
        self.minLength = kwargs.get('minLength', None)
        self.maxLength = kwargs.get('maxLength', None)
        self.charsAllowed = kwargs.get('charsAllowed', None)

    def defaultDefault(self):
        """ return the default value for the default value of the
        object.
        """
        return ""

    def convertValue(self, v):
        return str(v)

    def errorMsg(self, fs):
        msg = "Value '{}' ".format(fs)

        if self.minLength!=None and len(fs)<self.minLength:
            msg += "must be at least %d characters long"%self.minLength
            return msg

        if self.maxLength!=None and len(fs)>self.maxLength:
            msg += "must be no longer than %d characters"%self.maxLength
            return msg

        if self.charsAllowed!=None:
            for ch in fs:
                if ch not in self.charsAllowed:
                    msg += ("may only contain chars in: %s"
                            % self.charsAllowed)
                    return msg

        return super(StrField, self).errorMsg(fs)



#---------------------------------------------------------------------

class TextAreaField(StrField):
    """ a string field displayed using a textarea element """

    def readArgs(self, **kwargs):
        super(TextAreaField, self).readArgs(**kwargs)
        self.rows = kwargs.get('rows', 2)
        self.cols = kwargs.get('cols', 30)

    def formField(self, v):
        """ return html for a form field for this fieldInfo """
        h = form(('<textarea  class=gin id="id_{fieldName}" name="{fieldName}"'
                  ' rows="{rows}" cols="{cols}">'
                  '{v}</textarea>'),
            fieldName = self.fieldName,
            rows = self.rows,
            cols = self.cols,
            v = cgi.escape(v),
        )
        return h

#---------------------------------------------------------------------

class ChoiceField(StrField):
    """ A ChoiceFiled takes a choices argument of the form:
        choices=[('C', 'collection'),
                 ('D', 'delivery'),
                 ('N', 'none')]
    The 0th eleement of the tuple is the value of the field;
    the 1st is the displayed value. The default is the value of
    the initial tuple, unless a specific default is set.

    """

    def readArgs(self, **kwargs):
        super(ChoiceField, self).readArgs(**kwargs)
        self.choices = kwargs.get('choices',
            (('N','No'),('Y','Yes'))
        )
        if not kwargs.has_key('default'):
            self.defaultValue = self.choices[0][0]

    def formField(self, v):
        import mongoab
        """ return html for a form field for this fieldInfo
        @param v [ObjectId] the value in the field for the MonDoc
        @return [str] containing html
        """
        h = form("<select id='id_{fieldName}' name='{fieldName}'>\n",
            fieldName = self.fieldName
        )
        for choiceVal, choiceStr in self.choices:
            selected = ""
            if v == choiceVal:
                selected = " selected='selected'"
            hop = form("<option value='{cv}'{selected}>{cs}</option>\n",
                cv = choiceVal,
                cs = choiceStr,
                selected = selected)
            h += hop
        #//for
        h += "</select>\n"
        return h


#---------------------------------------------------------------------

class PostcodeField(StrField):
    """ a field holding a Python str holding a UK postcode
    The postcode regex came from:
    <http://stackoverflow.com/questions/164979/uk-postcode-regex-comprehensive>
    """

    def readArgs(self, **kwargs):
        super(PostcodeField, self).readArgs(**kwargs)
        self.fieldLen = kwargs.get('fieldLen', 20)

    validRegexp = re.compile(
        r"^[A-Z][A-Z]?\d[A-Z0-9]?\s?[0-9][A-Z][A-Z]$",
        flags = re.IGNORECASE)

    def isValidValue(self, s):
        if not isinstance(s, str): return False
        return self.validRegexp.match(s)

    def convertValue(self, v):
        return str(v).strip().upper()

    def formField(self, v):
        h = form('''<input class=gin id="id_{fieldName}" name="{fieldName}" type="text" size={fieldLen} value={v}>''',
            fieldName = self.fieldName,
            v = saxutils.quoteattr(str(v)),
            fieldLen = self.fieldLen,
        )
        return h

    def errorMsg(self, fs):
        if fs == "":
            # empty postcodes are allowed
            return ""

        if not self.validRegexp.match(fs):
            return "'{}' is not a valid postcode".format(fs)
        return super(PostcodeField, self).errorMsg(fs)

#---------------------------------------------------------------------

class BoolField(FieldInfo):
    """ a field holding a Python bool """

    def defaultDefault(self):
        """ return the default value for the default value of the
        object.
        """
        return False

    def isValidValue(self, v):
        return type(v)==bool

    def convertValue(self, v):
        print "~~~~~ convertValue v=%r ~~~~~" % (v,)
        return bool(v)

    def formField(self, v):
        """ return  html for a form field for this fieldInfo
        """
        checked = ""
        if v: checked = " checked"
        h = form('''<input id="id_{fieldName}" type="checkbox"
            name="{fieldName}"{checked}>''',
            fieldName = self.fieldName,
            checked = checked,
        )
        return h

    def readOnlyField(self, v):
        h = "<span class='read-only'>{}</span>".format(
            "yes" if v else "no")
        return h


#---------------------------------------------------------------------

class IntField(FieldInfo):
    """ a field holding a Python int """

    def readArgs(self, **kwargs):
        super(IntField, self).readArgs(**kwargs)
        self.fieldLen = kwargs.get('fieldLen', 12)
        self.minValue = kwargs.get('minValue', None)
        self.maxValue = kwargs.get('maxValue', None)

    def defaultDefault(self):
        """ return the default value for the default value of the
        object.
        """
        return 0

    def isValidValue(self, v):
        return type(v)==int

    def convertValue(self, v):
        return int(v)

    def formField(self, v):
        """ return  html for a form field for this fieldInfo """
        h = form('''<input class=gin id="id_{fieldName}" name="{fieldName}"
            type="number" size={fieldLen} value={v}>''',
            fieldName = self.fieldName,
            v = saxutils.quoteattr(self.formatStr.format(v)),
            fieldLen = self.fieldLen,
        )
        return h

    def errorMsg(self, fs):
        try:
            v = int(fs)
            # it worked, return "" to say so
        except:
            errMsg = "Value '{}' must be an integer".format(fs)
            return errMsg
        if self.minValue!=None and v<self.minValue:
            return "%d must be >= %d"% (v, self.minValue)
        if self.maxValue!=None and v>self.maxValue:
            return "%d must be <= %d"% (v, self.maxValue)
        return super(IntField, self).errorMsg(fs)

#---------------------------------------------------------------------

class FloatField(FieldInfo):
    """ a field holding a Python float """

    def readArgs(self, **kwargs):
        super(FloatField, self).readArgs(**kwargs)
        self.fieldLen = kwargs.get('fieldLen', 15)
        self.formatStr = kwargs.get("formatStr", "{:g}")
        self.minValue = kwargs.get('minValue', None)
        self.maxValue = kwargs.get('maxValue', None)

    def defaultDefault(self):
        """ return the default value for the default value of the
        object.
        """
        return 0.0

    def isValidValue(self, v):
        return type(v)==float or type(v)==int

    def convertValue(self, v):
        return float(v)

    def formField(self, v):
        """ return  html for a form field for this fieldInfo """
        h = form('''<input class=gin id="id_{fieldName}" name="{fieldName}" type="number" size={fieldLen} value={v}>''',
            fieldName = self.fieldName,
            v = saxutils.quoteattr(self.formatStr.format(v)),
            fieldLen = self.fieldLen,
        )
        return h

    def errorMsg(self, fs):
        try:
            v = float(fs)
            # it worked, return "" to say so
        except:
            errMsg = "Value '{}' must be a floating point number".format(
                fs
            )
            return errMsg

        if self.minValue!=None and v<self.minValue:
            return "%g must be >= %g"% (v, self.minValue)

        if self.maxValue!=None and v>self.maxValue:
            return "%g must be <= %g"% (v, self.maxValue)

        return super(FloatField, self).errorMsg(fs)

#---------------------------------------------------------------------

class HhmmssField(FieldInfo):
    """ a field holding a string of the form 'hh:mm:ss' e.g.
    '13:45:59'.
    """

    def readArgs(self, **kwargs):
        super(HhmmssField, self).readArgs(**kwargs)
        self.fieldLen = kwargs.get('fieldLen', 8)

    validRegexp = re.compile("^[0-2][0-9]:[0-9][0-9]:[0-9][0-9]$")

    def defaultDefault(self):
        """ return the default value for the default value of the
        object.
        """
        return "00:00:00"

    def isValidValue(self, s):
        if not isinstance(s, str): return False
        return validRegexp.match(s)

    def convertValue(self, s):
        """ the string representation in a form is the same as the format
        stored in the object.
        """
        return s

    def formField(self, v):
        """ return html for a form field for this fieldInfo """
        h = form('''<input class=gin id="id_{fieldName}" name="{fieldName}" type="text" size={fieldLen} value={v}>''',
            fieldName = self.fieldName,
            v = saxutils.quoteattr(str(v)),
            fieldLen = self.fieldLen,
        )
        return h

    def errorMsg(self, fs):
        if not self.validRegexp.match(fs):
            return "'{}' must be in the format hh:mm:ss".format(fs)
        return super(HhmmssField, self).errorMsg(fs)

#---------------------------------------------------------------------

class KeyField(FieldInfo):
    """ a field holding a key to a MongoAB document
    """

    def __init__(self, monDocClass, **kwargs):
        self.index = fieldIndex()
        self.monDocClass = monDocClass
        self.desc = ""
        self.null = True
        self.readArgs(**kwargs)

    def readOnlyField(self, v):
        import mongoab
        doc = self.monDocClass.getDoc(v)
        name = ""
        if doc: name = doc.name
        h = cgi.escape(name)
        return h

    def formField(self, v):
        import mongoab
        """ return html for a form field for this fieldInfo
        @param v [ObjectId|str] the value in the field for the MonDoc
        @return [str] containing html
        """
        h = form("<select id='id_{fieldName}' name='{fieldName}'>\n",
            fieldName = self.fieldName
        )
        #prvars("self.fieldName self.null v")
        if self.null:
            selected = ""
            if v==None: selected = " selected='selected'"
            h += form("<option value=''{selected}>(none)</option>\n",
                selected = selected)
        for op in self.monDocClass.find():
            #prvars("op")
            selected = ""
            if v != None and v == op._id:
                selected = " selected='selected'"
            hop = form("<option value='{id}'{selected}>{v}</option>\n",
                id = op.id(),
                v = op.__unicode__(),
                selected = selected)
            h += hop
        #//for
        h += "</select>\n"
        return h

    @printargs
    def convertValue(self, v):
        """ Convert a value from the form returned by the html form
        into an object of the type held in this field's value in the
        document.
        """
        import mongoab
        return mongoab.normaliseId(v)

    @printargs
    def getOb(self, v):
        return self.monDocClass.getDoc(v)


#---------------------------------------------------------------------

class ColumnBreak(FieldInfo):

    def readOnlyField(self, v):
        return ""

    def formField(self, v):
        return ""

    def formLine(self, v, readOnly=False):
        return ""

#---------------------------------------------------------------------




#end
