/* app.js */

//--------------------------------------------------------------------
/* help pages */

function openHelp(helpPage){
    /* open a help page in a new window */
    url = "/help/" + helpPage;
    open(url, "help",
        "width=500, height=600,resizable=1,scrollbars=1,"
        + "menubar=0,personalbar=0,toolbar=1");

}

//--------------------------------------------------------------------
/* editting on wikiedit page */

function addAround(b, a) {
    /* add text before and after the selected text */ 
    ($("#source")
        .selection('insert', {text: b, mode: 'before'})
        .selection('insert', {text: a, mode: 'after'}));  
}    

function addTable() {
    var t = ("\nHead 1 | Head 2 | Head 3\n"    
        +      "------ | ------ | ------\n"  
        +      "cell 1 | cell 2 | cell 3\n"  
        +      "cell 4 | cell 5 | cell 6\n");
    addAround(t, "");
}    



//--------------------------------------------------------------------

//end