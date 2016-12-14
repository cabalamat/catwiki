/* jsfunctions.js */

/*****
Some javascript utility functions
*****/

//--------------------------------------------------------------------

function ObjToSource(o){
    if (!o) return 'null';
    if (typeof(o) == "object") {
        if (!ObjToSource.check) ObjToSource.check = new Array();
        for (var i=0, k=ObjToSource.check.length ; i<k ; ++i) {
            if (ObjToSource.check[i] == o) {return '{}';}
        }
        ObjToSource.check.push(o);
    }
    if (typeof(o) == "string"){
        return JSON.stringify(o);
    }
    var k="";
    var na=typeof(o.length)== "undefined" ? 1 : 0;
    var str="";
    for(var p in o){
        if (na) k = "'"+p+ "':";
        if (typeof o[p] == "string") str += k + "'" + o[p]+"',";
        else if (typeof o[p] == "object") str += k + ObjToSource(o[p])+",";
        else str += k + o[p] + ",";
    }
    if (typeof(o) == "object")
        ObjToSource.check.pop();

    if (na)
        return "{"+str.slice(0,-1)+"}";
    else
        return "["+str.slice(0,-1)+"]";
}

function toString(ob){
    /* convert an object to a string */
    return ObjToSource(ob);
}

//--------------------------------------------------------------------
/* functions on objects and arrays */

function dokv(ob, doSomething){
    /* do on keys and values
    */
    for (var property in ob) {
        if (ob.hasOwnProperty(property)) {
            var value = ob[property];
            doSomething(property, value);
        }
    }
}

function get(ob, key, value){
    /* If object (ob) has a property (key), then return it, else
    return (value)
    */
    if (ob.hasOwnProperty(key))
        return ob[key];
    else
        return value;
}

function contains(haystack, needle){
    for (var i=0; i<haystack.length; i++){
        if (haystack[i]===needle) return true;
    }
    return false;
}

function remove(a, item){
    /* remove all occurrances of (item) from array (a) */
    return a.filter(el => el!==item);
}


function including(a, item) {
    /* return an array like (a) but containing item (item).
    If it alrady contains it, just return (a).
    Else return a new array with (item) in it.
    */
    if (contains(a, item)) {
        return a;
    } else {
        var clone = a.slice(0);
        clone.push(item);
        return clone;
    }
}

function makeIdDict(obs){
    /*
    obs::[Object] has an 'id' key
    returns::{str:Object} where the keys are the ids
        from (obs)
    */
    var idDict = {};
    obs.forEach(ob => {
        var id = get(ob, 'id', "");
        if (id !== ""){
            idDict[id] = ob;
        }
    });
    return idDict;
}

function minimum(a){
    /* return the minimum value in an array */
    if (a.length===0) return null;
    var min;
    var first = true;
    a.forEach(e => {
        if (first){
            min = e;
        } else {
            if (e < min) min = e;
        }
        first = false;
    });
    return min;
}

//--------------------------------------------------------------------
/* functions on strings */

function removeSpaces(s) {
    /* return a string like (s) but with all spaces removed */
    return s.replace(/ /g, "");
}

//--------------------------------------------------------------------
/*****
From http://stackoverflow.com/questions/5560248
     /programmatically-lighten-or-darken-a-hex-color-or-rgb-and-blend-colors

p = proportion of conversion
from = from colour
to = to colour

*****/

function blendColors(c0, c1, p) {
    var f=parseInt(c0.slice(1),16),
    t=parseInt(c1.slice(1),16),
    R1=f>>16,
    G1=f>>8&0x00FF,
    B1=f&0x0000FF,
    R2=t>>16,
    G2=t>>8&0x00FF,
    B2=t&0x0000FF;
    return "#"+(0x1000000+(Math.round((R2-R1)*p)+R1)*0x10000
    +(Math.round((G2-G1)*p)+G1)*0x100+(
    Math.round((B2-B1)*p)+B1)).toString(16).slice(1);
}

/*
percent of 0...1 = lighten
percent of 0...-1 = darken
*/
function shadeColor2(color, percent) {
    var f=parseInt(color.slice(1),16),t=percent<0?0:255,p=percent<0?percent*-1:percent,R=f>>16,G=f>>8&0x00FF,B=f&0x0000FF;
    return "#"+(0x1000000+(Math.round((t-R)*p)+R)*0x10000+(Math.round((t-G)*p)+G)*0x100+(Math.round((t-B)*p)+B)).toString(16).slice(1);
}

function lighten(col, amount) { return shadeColor2(col, amount); }
function darken(col, amount) { return shadeColor2(col, -amount); }


//--------------------------------------------------------------------

/* end */
