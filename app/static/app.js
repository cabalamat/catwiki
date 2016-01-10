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

//end