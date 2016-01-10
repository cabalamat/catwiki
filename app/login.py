# login.py = pages for dealling with logging in etc

from flask import request, redirect
from flask.ext.login import login_user, logout_user, current_user

import pymongo

import allpages
from allpages import *

import models


#---------------------------------------------------------------------

@app.route('/', methods=['POST', 'GET'])
def front():
    doc = models.User() #blank for now
    msg = "(no message)"

    if request.method=='POST':
        d = request.form
        doc = doc.populateFromForm(d,
            populateFieldsOnly=True)
        u = models.User.find_one({'userName': doc.userName})
        
        ok = u and models.verifyPassword(u.hashedPassword,
                                         doc.password)
        if ok:
            login_user(u)
        else:        
            msg = ("<span style='color:#800; background:#fee;'>"
                   "<i class='fa fa-times-circle'></i> "
                   "login failed</span>")
    frontPageTem = jinjaEnv.get_template("front_page.html")
    h = frontPageTem.render(
        badLoginWarning = "",
        #badLoginWarning
    )
    return h

#---------------------------------------------------------------------

@app.route('/logout')
def logout():
    logout_user()
    return redirect("/")

#---------------------------------------------------------------------

@app.route('/users')
def users():
    usersTem = jinjaEnv.get_template("users.html")
    h = usersTem.render(
        table = usersTable(),
        count = models.User._collection.count(),
    )
    return h

def usersTable():
    """ returns an html table of users """
    h = """<table class='report_table'>
<tr>
   <th class=debug>(id)</th>
   <th>User name</th>
   <th>Is admin?</th>
</tr>
"""
    for doc in models.User.find(sort=[('userName',pymongo.ASCENDING)]):
        prvars("doc")

        item = form("""<tr>
<td class="debug unemphasized">{id}</td>
<td><a href="/user/{id}">{userName}</a></td>
<td>{isAdmin}</td>
<td><a href='/user/{id}'><i class='fa fa-edit'></i> edit</a></td>
</tr>""",
            id = doc.id(),
            userName = htmlEsc(doc.userName),
            isAdmin = yn(doc.isAdmin),
        )
        h += item
    #//for
    h += "</table>\n"
    return h

def yn(b):
    if b:
        return "Yes"
    else:
        return "No"

def orNone(s):
    if s:
        return htmlEsc(s)
    else:
        return "<span class='unemphasized'>None</span>"
    
#---------------------------------------------------------------------


@app.route('/user/<id>', methods=['POST', 'GET'])
def user(id):
    if id=="NEW":
        doc = models.User()
        prvars("doc")
    else:
        doc = models.User.getDoc(id)
        prvars("doc")

    if request.method=='POST':
        d = dict([(k, request.form[k])
                  for k in request.form.keys()])
        doc = doc.populateFromForm(d,
            populateFieldsOnly=True)

        if d['delete'] == u"1":
            # delete this record
            print "** about to remove id=%r" % (id,)
            doc.remove()
            return redirect("/users", code=302)
        else:
            # update this record
            print ("******** update form data = %r\ndoc = %r"
                   % (d, doc))
            doc.save()
            return redirect("/users", code=302)

    userTem = jinjaEnv.get_template("user.html")
    h = userTem.render(
        doc = doc,
        id = id,
        buildFormLines = doc.buildFormLines(),
    )
    return h



#---------------------------------------------------------------------




#end
