# Editing pages in CatWiki

## The Editing Toolbar

Above the text entry area is the editing toolbar. It looks like this:

> <i class='fa fa-bold'></i>
<i class='fa fa-italic'></i>
<i class='fa fa-strikethrough'></i>
<i class='fa fa-superscript'></i>
<i class='fa fa-subscript'></i>
<i class='fa fa-link'></i>
<i class='fa fa-image'></i>
<i class='fa fa-table'></i>

### Text formatting tools, <i class='fa fa-bold'></i> <i class='fa fa-italic'></i> <i class='fa fa-strikethrough'></i> <i class='fa fa-superscript'></i> <i class='fa fa-subscript'></i>

These tools allow you to format text. The tools are:

Tool | Selected text | Changes to | Looks like | Notes
-----| ------------- | ---------- | ---------- | -----
<i class='fa fa-bold'></i> | `abc` | `**abc**` | **abc** | bold type
<i class='fa fa-italic'></i> | `abc` | `*abc*` | *abc* | italic type
<i class='fa fa-strikethrough'></i> | `abc` | `<s>abc</s>` | <s>abc</s> | strikethrough
<i class='fa fa-superscript'></i> | `abc` | `a<sup>b</sup>c` | a<sup>b</sup>c | superscript - only middle character selected
<i class='fa fa-subscript'></i> | `H2O` | `H<sub>2</sub>O` | H<sub>2</sub>O | subscript - only middle character selected

### Adding links to content, <i class='fa fa-link'></i> <i class='fa fa-image'></i>

These tools allow you to specify a hyperlikn or image.

Tool | Selected text | Changes to | Looks like | Notes
-----| ------------- | ---------- | ---------- | -----
<i class='fa fa-link'></i> | `abc` | `[abc]()` | [abc]() | hyperlink, url left blank
<i class='fa fa-image'></i> | `abc` | `![abc](img)` | ![abc](img) | image, "img" is placeholder for image URL

The hyperlink tool ( <i class='fa fa-link'></i> ) uses the linked text as the displayed text for a hyperlink. The user has to manually add the URL within the `()`.

The image tool ( <i class='fa fa-image'></i> ) uses the linked text as the alt text for the image. The user has to replace the `img` within `(img)` with the actual
URL for the image.

### The Table tool, <i class='fa fa-table'></i>

The table tool ( <i class='fa fa-table'></i> ) works differently from the others. It inserts a table with 3 columns and 3 rows, like this:
```
Head 1 | Head 2 | Head 3
------ | ------ | ------
cell 1 | cell 2 | cell 3
cell 4 | cell 5 | cell 6
```

The table looks like this:

Head 1 | Head 2 | Head 3
------ | ------ | ------
cell 1 | cell 2 | cell 3
cell 4 | cell 5 | cell 6







