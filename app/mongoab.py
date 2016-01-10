
# mongoab.py = mongo DB abstraction layer

"""
A lightweight abstraction layer around pymongo.

Deals with:
* automatic conversion between str/ObjectId for _id fields
* allows field names to be specified using dot notation, i.e.
  ``doc.foo`` instead of ``doc['foo']``.
* default values and validation of fields
* to directly talk to the pymongo collection, use _collection.

"""

import UserDict
import collections

import pymongo
mongoClient = pymongo.MongoClient()
from bson.objectid import ObjectId

from ulib.debugdec import *
from monfield import *

#---------------------------------------------------------------------
# creating identifiers for Mongo DB documents

class MongoabIncrementor:
    """ Increments a number. Used to create a unique index number
    for mongo DB databases.

    Stores value in collection 'mongoab', document id 'lastIndex'.
    """

    def __init__(self, database):
        self.database = database
        self.index = self.getIndexFromDB()

    def getIndexFromDB(self):
        mongoabCol = self.database.mongoab
        lastIndexDoc = mongoabCol.find_one({'_id':'lastIndex'})
        if lastIndexDoc == None:
            index = 1
        else:
            index = lastIndexDoc.get('value', 1)
        return index

    def __call__(self):
        print "in MongoabIncrementor, index was %d" % (self.index,)
        self.index += 1
        self.database.mongoab.save({
            '_id': 'lastIndex',
            'value': self.index})
        return self.index


database = None   # the database mongoab is working with
idInc = None      # used to increment _id values

def setDatabase(dbStr):
    global database, idInc
    database = mongoClient[dbStr]
    idInc = MongoabIncrementor(database)

#---------------------------------------------------------------------

class MonDocMeta(type):

    def __init__(cls, name, bases, dyct):
        super(MonDocMeta, cls).__init__(name, bases, dyct)

        cls.classInfo = Struct()
        doStuff(cls, dyct)

def doStuff(cls, dyct):
    cls.classInfo.fieldNameSet = set()
    cls.classInfo.fieldNameTuple = []
    for fieldName, fieldInfo in dyct.items():
        if not isinstance(fieldInfo, FieldInfo): continue
        fieldInfo.fieldName = fieldName
        cls.classInfo.fieldNameSet.add(fieldName)
        cls.classInfo.fieldNameTuple.append(fieldName)
    #//for
    def keyFn(fieldName):
        return dyct[fieldName].index
    cls.classInfo.fieldNameTuple = tuple(
        sorted(cls.classInfo.fieldNameTuple,
               key= keyFn))


validObjectId = re.compile("[0-9a-fA-F]{24}")
def isObjectIdStr(s):
    """ Is (s) a string that came from an ObjectId (24 hex digits?)
    @return [bool]
    """
    if not(isinstance(s, str) or isinstance(s, unicode)):
        return False
    return bool(validObjectId.match(s))

def normaliseId(id):
    """ normalise an id. if it is convertable to an ObjectId, do
    so. Else keep it as it is.
    """
    if isObjectIdStr(id):
        return ObjectId(id)
    return id

def normaliseCol(colName):
    """ normalise a collection """
    if type(colName)==str:
        return database[colName]
    elif type(colName)==unicode:
        return database[str(colName)]
    else:
        return colName

#---------------------------------------------------------------------
""" Abstraction around a Mongo DB document
    ======================================

## Connecting to Mongo DB ##

find() = get some documents from the collection.
This is a thin wrapper around pymongo's find() method.
Called with no arguments it returns all the documents in the
collection.

find_one() = get a document from the collection.
This is a thin wrapper around pymongo's find_one() method.

getDoc() = get a document based on its _id

save() = save document.
If it doesn't have an _id, a new document will be created in
the database and it given an _id.

remove() = delete the document.
Removes the document in the collection that has the same _id
as this one. So if this document has no id, nothing happens.


## Interacting with the document ##

As with pymongo, fields can be accessed with doc['fieldName'].

But you can also use doc.fieldName, which is shorter and more
intuitive.


## interacting with HTML, including forms ##

If fields have been defined with the FieldInfo classes in monfield,
HTML forms can be built automatically, using buildFormLines().

When there is an http POST request, this can be used to populate
the document, using populateFromForm()

a() returns HTML containing an a-href for the document. It requires
the subclass to have implemented a url() functiion. It also relies
upon the name() function which returns the contents of the first
field defined with monfield.

getName() returns the contents of the first field defined with
monfield. By convention this is a string containing a human-
understandable name for the document. The field is often called 'name',
but it doesn't have to be.

"""

class MonDoc(object, UserDict.DictMixin):
    """ an abstraction over a Mongo Document """

    __metaclass__ = MonDocMeta

    def __init__(self):
        self.populateFields()

    def populateFields(self):
        """ populate the fields defined in the subclass's definition.
        """
        classDict = dict(type(self).__dict__)
        for con, co in classDict.items():
            if con[:1] == "_": continue
            if isinstance(co, FieldInfo):
                self.__dict__[con] = co.createWithInitialValue()
        #//for

    def __repr__(self):
        """ this consists of:
        * the class name
        * the _id (if there is one)
        * the contents of the first field (which will typically be a
          human-readable name for the object.
        """
        result = "<%s" % self.__class__.__name__
        if self.hasId():
            result += " %s" % (self._id,)
        if len(self.classInfo.fieldNameTuple)>0:
            fn0 = self.classInfo.fieldNameTuple[0]
            v = self.get(fn0)
            result += " %s=%r" % (fn0, v)
        if 1:
            for fn in self.classInfo.fieldNameTuple[1:]:
                v = self.get(fn)
                result += " %s=%r" % (fn, v)
        result += ">"
        return result

    #========== dealing with FieldInfo ==========

    @classmethod
    def getFieldInfo(cls, fieldName):
        """
        @param fieldName [str]
        @return [FieldInfo]
        """
        return cls.__dict__[fieldName]

    @classmethod
    def hasFieldInfo(cls, fieldName):
        """ does the class have a field called (fieldName)
        with FieldInfo in it?
        """
        return fieldName in cls.classInfo.fieldNameSet

    #========== talking to MongoDB ==========

    @classmethod
    def getCollection(cls, kwargs):
        """ get the collection for use in a class method, by
        looking in the kwargs.
        if it is there, remove it from the kwargs.
        @return tuple (col, b) where
           col::[pymongo.collection.Collection]
           b::[bool] = over-riding _collection
        """
        b = False
        if kwargs.has_key('useCollection'):
            colName = kwargs['useCollection']
            if type(colName) == unicode:
                colName = str(colName)
            if type(colName) == str:
                col = database[colName]
            else:
                col = colName # it's a collection object already
            del kwargs['useCollection']
            b = True
        else:
            col = cls._collection
        return col,b

    @classmethod
    def getCollectionToUse(cls, useCollection):
        """ get the collection for use in a class method
        @param useCollection [None|str|pymongo.collection.Collection]
        @return tuple (col, b) where
           col::[pymongo.collection.Collection]
           b::[bool] = over-riding _collection
        """
        if useCollection:
            if type(useCollection) == unicode:
                useCollection = str(useCollection)
            if type(useCollection) == str:
                col = database[useCollection]
            else:
                col = useCollection # it's a collection object already
            b = True
        else:
            col = cls._collection
            b = False
        return col,b

    @classmethod
    def find(cls, *args, **kwargs):
        #prvars("args kwargs")
        """ a wrapper round the pymongo find() method """
        col, b = cls.getCollection(kwargs)
        #prvars("kwargs col")
        cursor = col.find(*args, **kwargs)
        for item in cursor:
            ins = cls.transform(item)
            if b:
               ins._useCollection = col
            yield ins

    @classmethod
    def find_one(cls, *args, **kwargs):
        """ a wrapper round the pymongo find_one() method """
        #prvars("kwargs")
        col, b = cls.getCollection(kwargs)
        #prvars("kwargs")
        doc = col.find_one(*args, **kwargs)
        if doc==None: return None
        ins = cls.transform(doc)
        if b:
            ins._useCollection = col
        return ins

    @classmethod
    def transform(cls, mongoDoc):
        instance = cls()
        for k, v in mongoDoc.items():
            instance.__dict__[k] = v
        return instance

    @classmethod
    def getDoc(cls, id, createIfNotExist=False, useCollection=None):
        """ get a document from the collection given its id.
        If it doesn't exist, return None
        @param id [str|ObjectId]
        @param createIfNotExist [bool] if the document doesn't exist,
            create a new one and set its _id to be id.
        """
        col, b = cls.getCollectionToUse(useCollection)
        if isObjectIdStr(id):
            id = ObjectId(id)
        query = {'_id': id}
        result = col.find_one(query)
        if result==None:
            if createIfNotExist:
                instance = cls()
                instance._id = id
                if b: instance._useCollection = col
                return instance
            else:
                return None
        ins = cls.transform(result)
        if b: ins._useCollection = col
        return ins

    def remove(self, useCollection=None):
        """ remove this document from the database """
        if useCollection:
            col = normaliseCol(useCollection)
        else:
            col = self._collection
        if self.hasId():
            forDeletion = {'_id': self._id}
            col.remove(forDeletion)
        else:
            #do nothing
            pass
    delete = remove

    def preSave(self):
        """ The use can over-rde this with a method to be called
        immediatedly before the document is saved.
        """
        pass

    def save(self, useCollection=None):
        """ save or insert a document.
        If the document has an id, it will be put in the table
        over-writing the document with the existing id.

        If the document doesn't have an id, a new document will
        be put in the table, and its id put in self.

        @param useCollection [None|str|pymongo.collection] override
           cls._collection
        """
        if useCollection:
            self._useCollection = normaliseCol(useCollection)
        self.preSave()
        if self.hasId():
            # over-write existing document
            self.col().save(self.mongoDict())
        else:
            # create new document
            newId = "%s-%d" % (self.col().name, idInc())
            self._id = newId
            self.col().save(self.mongoDict())

    def mongoDict(self):
        """ return a dictionary for the current document,
        in the format wanted by pymongo.
        @return [dict]
        """
        d = self.__dict__
        if d.has_key('_useCollection'):
            d = dict(d)
            del d['_useCollection']
        return d

    def id(self):
        """ return this docment's _id, converted to a string.
        @return [str]
        """
        if self.hasId():
            return str(self._id)
        else:
            return ""

    def hasId(self):
        """ does this document have an _id field? """
        return self.__dict__.has_key('_id')

    def getOb(self, fn):
        """ get a field from this document, converting it to a
        doc if it is a reference to one (i.e. an ObjectId).
        @param fn [str] field name
        """
        v = self.get(fn)
        if not self.hasFieldInfo(fn): return v
        fi = self.getFieldInfo(fn)
        return fi.getOb(v)

    def col(self):
        """ return a document's collection """
        if self.__dict__.has_key('_useCollection'):
            return self._useCollection
        return self._collection

    #========== make it work like a dict ==========

    def __getitem__(self, key):
        return self.__dict__[key]

    def __setitem__(self, key, value):
        self.__dict__[key] = value

    def __delitem__(self, key):
        del self.__dict__[key]

    def keys(self):
        return self.__dict__.keys()

    def __iter__(self):
        for item in self.__dict__:
            yield item

    def __len__(self):
        return len(self.__dict__)

    def get(self, key, defaultValue=None):
        if self.__dict__.has_key(key):
            return self.__dict__[key]
        else:
            return defaultValue

    #========== html and forms ==========

    def buildForm(self, **kwargs):
        """ build all the form, excluding buttons.
        Arguments in kwargs are:
        - readOnly [bool], defaults to False. Make the form read-only.
        - withErrors [bool], defaults to False. If true, check for errors
          in the user's input and display them in the form.
        - userData [dict] only used if withErrors==True, the user's input
          data.
        """
        twoColumn = self.formIsTwoColumn()

        if twoColumn:
            h = ("<table><tr><td class='two-columns'>\n"
                 "<table class='form-table'>\n")
        else:
            h = "<table class='form-table'>\n"

        for fieldName in self.classInfo.fieldNameTuple:
            fieldInfo = self.getFieldInfo(fieldName)
            if isinstance(fieldInfo, ColumnBreak):
                h += """</table>
                     </td><td class='two-columns second-column'>
                     <table class="form-table">"""
            else:
                if kwargs.has_key('userData'):
                    kwargs['userDataForField'] = (
                        kwargs['userData'].get(fieldName, ""))
                h += fieldInfo.formLine2(self.get(fieldName), **kwargs)
        #//for
        if twoColumn:
            h += ("</table></td></tr></table>\n")
        else:
            h += "</table>\n"
        return h

    def formLine(self, fieldName, **kwargs):
        fieldInfo = self.getFieldInfo(fieldName)
        h = fieldInfo.formLine2(self.get(fieldName), **kwargs)
        return h

    def formIsTwoColumn(self):
        """ is the form 2-column
        @return [bool]
        """
        return True
        for fieldName in self.classInfo.fieldNameTuple:
            fieldInfo = self.getFieldInfo(fieldName)
            if isinstance(fieldInfo, ColumnBreak):
                return True
        return False

    def buildLeftFormLines(self, readOnly=False):
        """ Build the left column of the form (for a two column form)
        @return [str] containing html
        """
        h = ""
        gotColumnBreak = False
        for fieldName in self.classInfo.fieldNameTuple:
            fieldInfo = self.getFieldInfo(fieldName)
            prvars("fieldName fieldInfo gotColumnBreak")
            if isinstance(fieldInfo, ColumnBreak):
                gotColumnBreak = True
            if not gotColumnBreak:
                h += fieldInfo.formLine(self.get(fieldName), readOnly)
        return h

    def buildRightFormLines(self, readOnly=False):
        """ Build the right column of the form (for a two column form)
        @return [str] containing html
        """
        h = ""
        gotColumnBreak = False
        for fieldName in self.classInfo.fieldNameTuple:
            fieldInfo = self.getFieldInfo(fieldName)
            if isinstance(fieldInfo, ColumnBreak): gotColumnBreak = True
            if gotColumnBreak:
                h += fieldInfo.formLine(self.get(fieldName), readOnly)
        return h

    def buildFormLines(self, readOnly=False):
        """ return html containing a partial html array for a form.
        Each line in the form is a table row containing two table
        boxes.

        @param readOnly [bool] form is read-only
        @return [str] containing html
        """
        h = ""
        for fieldName in self.classInfo.fieldNameTuple:
            fieldInfo = self.getFieldInfo(fieldName)
            h += fieldInfo.formLine(self.get(fieldName), readOnly)
        return h

    def buildFormLinesWithErrors(self, formData):
        """ return html containing a partial html array for a form.
        Each line in the form is a table row containing two table
        boxes. This method is being called because the data in the
        form (in formData) probably has errors in it. These errors will
        be reflected on the html output.

        @param formData [dict] containing data from the form
        @return [str] containing html
        """
        h = ""
        for fieldName in self.classInfo.fieldNameTuple:
            fieldInfo = self.getFieldInfo(fieldName)
            if formData.has_key(fieldName):
                h += fieldInfo.formLineWithErrors(
                    self.get(fieldName),
                    formData[fieldName])
            else:
                h += fieldInfo.formLine(self.get(fieldName))
        return h

    def formValid(self, formData):
        """ is the data coming back from the form valid for this
        document?
        @param formData [dict]
        @return [bool]
        """
        for fieldName in self.classInfo.fieldNameTuple:
            if formData.has_key(fieldName):
                fieldInfo = self.getFieldInfo(fieldName)
                errMsg = fieldInfo.errorMsg(formData[fieldName])
                if errMsg: return False
        #//for
        return True

    def errorMessage(self):
        """ Validate the document as a whole (over and above any per-
        field validation that may also occur). If it is valid (i.e.
        if all the fields are consistent with each other), return "",
        else return an appropriate error message.

        This should be over-ridden by subclasses where appropriate.

        @return [str]
        """
        return ""


    #@printargs
    def populateFromForm(self, form, populateFieldsOnly=True):
        """ create a new object like the current one, populated
        from the form (form).
        @param form [dict]
        @param populateFieldsOnly [bool] if this is set, then only
             if a field in the form has the same name as a field in
             the class definition is it copied across (i.e. new fields
             aren't created).
        @return [MonDoc]
        """
        formDict = dict([(k, form[k])
                         for k in form.keys()])
        newOb = self
        newOb.__dict__ = self.__dict__.copy()
        for k,v in formDict.items():
            if (not populateFieldsOnly
                or (self.hasFieldInfo(k))):
                try:
                    self.setField(k, v)
                except:
                    pass
        # get a list of the fields that the doc has fieldInfo for but which
        # weren't returned from the form, Then populate them via the fieldInfo
        # object. This is important because HTML forms only send info for
        # checkboxes that are checked
        formFieldSet = set(formDict.keys())
        fieldNameSet = set(fn
                           for fn in self.classInfo.fieldNameTuple
                           if type(self.getFieldInfo(fn)) == BoolField)
        notInForm = fieldNameSet - formFieldSet
        for fn in notInForm:
            self.setField(fn, None)
        return newOb

    def a(self):
        """ get an a-href for a document """
        return "<a href='%s'>%s</a>" % (self.url(), self.getName())

    def getName(self):
        """ Returns the contents of the first field defined with
        monfield. By convention this is a string containing a human-
        understandable name for the document.

        The field often has the fieldName 'name', but it doesn't have to.
        @return [str|unicode]
        """
        if len(self.classInfo.fieldNameTuple)==0:
            return ""
        fn0 = self.classInfo.fieldNameTuple[0]
        fi0 = self.getFieldInfo(fn0)
        v = self.get(fn0, "")
        if type(v)==str or type(v)==unicode: return v
        return unicode(str(v), 'utf-8')


    #========== misc ==========

    def __unicode__(self):
        """ the default value is the value of the
        first field.
        @return [unicode]
        """
        if len(self.classInfo.fieldNameTuple)==0: return u""
        fn0 = self.classInfo.fieldNameTuple[0]
        fi0 = self.getFieldInfo(fn0)
        v = self.get(fn0)
        if type(v)==unicode: return v
        return unicode(v, 'utf-8')

    def __getattr__(self, name):
        """ we haven't found the attribute name, so return a
        default value of None.
        """
        return None

    def setField(self, fieldName, newValue):
        if self.hasFieldInfo(fieldName):
            # a defined field, validate it
            fieldInfo = self.getFieldInfo(fieldName)
            #prvars("fieldInfo newValue")
            self.__dict__[fieldName] = fieldInfo.convertValue(newValue)
        else:
            # not a defined field, just set it
            self.__dict__[fieldName] = newValue

    def isFieldValid(self, fieldName):
        fieldInfo = self.getFieldInfo(fieldName)
        return fieldInfo.isValidValue(self[fieldName])



#---------------------------------------------------------------------

class BadMongoabId(Exception): pass

def getDoc(id):
    """ Get a document from a database given its id. The id
    must be of the form {collectionName}-{integer} where collectionName
    is the name of the collection of which it is a part.

    Note that this method returns a MonDoc and not a subclass of MonDoc
    (such as vehicle.Vehicle, req.Req, etc). It would not be difficult
    to modify this so that subclasses were registered and the appropriate
    one used, however we have not done so here as it would introduce
    complexity to the system.

    @param id [str] a database-wide unique id
    @return [MonDoc|None] if not findable, returns None
    """
    ix = id.find('-')
    if ix<0: raise BadMongoabId()
    collectionName = id[:ix]
    result = database[collectionName].find_one({'_id': id})
    if result==None: return None
    return MonDoc.transform(result)

#---------------------------------------------------------------------


#end
