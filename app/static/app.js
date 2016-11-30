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


function boldPressed(){
    console.log("boldPressed");
    
    var selectedText = getSelection();
    console.log("Selected: " + selectedText);
    
    var newText = "**" + selectedText + "**";
}

function getSelection() {
    
    // obtain the object reference for the <textarea>
    var txtarea = document.getElementById("source");
    
    // obtain the index of the first selected character
    var start = txtarea.selectionStart;
    
    // obtain the index of the last selected character
    var finish = txtarea.selectionEnd;
    
    // obtain the selected text
    var sel = txtarea.value.substring(start, finish);
    
    return sel;
}
//--------------------------------------------------------------------

//end