/* app.js */

//--------------------------------------------------------------------
/* help pages */

function openHelp(helpPage){
    /* open a help page in a new window */
    var url = "/help/" + helpPage;
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

function blockquote() {
    var sel = $('#source').selection(); // selected text
    var lines = sel.split("\n");
    //console.log("lines=" + toString(lines));
    var bqLines = lines.map(line => {
        return "> " + line;
    });
    //console.log("bqLines=" + toString(bqLines));
    var bqSel = bqLines.join("\n");
    $('#source').selection('replace', {text: bqSel});
}

function bulletList() {
    var sel = $('#source').selection();
    var lines = sel.split("\n");
    var rLines = lines.map(line => {
        return "* " + line;
    });
    var r = rLines.join("\n");
    $('#source').selection('replace', {text: r});
}

function numberedList() {
    var sel = $('#source').selection();
    var lines = sel.split("\n");
    var n = 1;
    var rLines = lines.map(line => {
        return (n++) + ". " + line;
    });
    var r = rLines.join("\n");
    $('#source').selection('replace', {text: r});
}

function monospace() {
    /* Make text monospace. If it is all on one line, suround with `...`,
    else suround with ```...``` */
    var sel = $('#source').selection();
    var lines = sel.split("\n");
    if (lines.length <= 1){
        addAround("`", "`");
    } else {
        addAround("\n```\n", "\n```\n");
    }
}

//--------------------------------------------------------------------

//end
