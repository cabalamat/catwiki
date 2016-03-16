# Markdown syntax

*This page describes the version of markdown syntax used by Sitebox. See also [[extensions]].*

Below is a table of contents. It can be produced using the markup `[TOC]`.

[TOC]

## Images

Inline-style: 

    ![alt text](url/goes/here.png "The Title")

## Source code

Text with `tt` some computer `code` in it.

Python source code:

```python
def convertQuickLinks(s):
    """ Converts [[xxx]] -> [xxx](xxx)
    @param s [str] containing markdown source
    @return [str]
    """
    QUICKLINK_RE = r"\[\[([A-Za-z0-9_ ]+)\]\]"
    REPLACE_WITH = r"[\1](\1)"
    r = re.sub(QUICKLINK_RE, REPLACE_WITH, s)
    return r
```

## Tables

Here is a table:

First Header  | Second Header
------------- | -------------
Content Cell  | Content Cell
Content Cell  | Content Cell

And here's another:

| Function name | Description                    |
| ------------- | ------------------------------ |
| `help()`      | Display the help window.       |
| `destroy()`   | **Destroy your computer!**     |

## Markup within a paragraph

This includes *italic*, **bold**, and `monospaced` text. 