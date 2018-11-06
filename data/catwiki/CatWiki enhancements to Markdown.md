# CatWiki enhancements to Markdown

[CatWiki](home) uses the [Python-Markdown](https://pythonhosted.org/Markdown/) implementation of [[Markdown]], with the following extensions:

* [extra](https://pythonhosted.org/Markdown/extensions/extra.html) -- various improvements
* [sane_lists](https://pythonhosted.org/Markdown/extensions/sane_lists.html) -- alters the behaviour of the Markdown List syntax to be less surprising
* [toc](https://pythonhosted.org/Markdown/extensions/toc.html) -- allows for a table of contents
* [codehilite](https://pythonhosted.org/Markdown/extensions/code_hilite.html) -- highlights code using [Pygments](http://pygments.org/)

## MediaWiki-style links

In addition, CatWiki also allows MediaWiki-style links, i.e. starting with `[[` and ending with `]]`; within these links, allowed characters are letters (`A-Za-z`), digits (`0-9`), spaces, underlines (`_`), hyphens (`-`) and periods (`.`). 

Articles names in MediaWiki-style links can use different capitalisation and will link to the same article, E.g. consider this sentence:

> There is a [[FAQ]] or [[faq]].

Both links go to the same article.


## See also

* [[Markdown]]
