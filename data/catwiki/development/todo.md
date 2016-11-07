# SiteBox To-do List

*This is my immediate to-do list. For a longer-term development schedule see [[long term development plan]]*.

A list of things to be done for SiteBox.

[TOC]

## Immediate

*The immediate goal is to get SiteBox to a state where it can be used like [MarkWiki](https://github.com/mblayman/markwiki)*.

Add a "Move page" or "Rename page" button, linked to a facility for [[redirection]] (like Mediawiki [has](http://www.mediawiki.org/wiki/Help:Redirects)).

Improve formatting / CSS to make it look nice. E.g. formating of monospaced text, code, and blockquotes. Add language-definable code highlighting for source code.

The name SiteBox can be confused with the [http://www.sitebox.com/](http://www.sitebox.com/) website. Change branding to MeowCat to avoid this and because I have the `meowc.at` domain. Perhaps use [this icon](http://www.flaticon.com/free-icon/kitty-front_23401) or something similar. See *[[MeowCat Cat Icons]]*.

On the [[redirection]] page, text with two `[[` followed by two `]]` is incorrectly rendered; fix this.

### Change rendering of markdown to HTML

Change Python-Markdown's TOC extension so that it takes parameters for what header-levels it puts into the TOC. (I want `h2`-`h5`; it uses `h1`-`h6`).

Add to Markdown the facility to indent a paragraph (MediaWiki uses `:` for this).

### Done

Add [Markdown extensions](Markdown/extensions) to SiteBox --DONE

Allow the existence of multiple sites; the list of sites should be browsable. Allow the existence of multiple roots for sites, i.e. some could be under `sitebox/data/` and some under `~/mylocalwiki/`, the latter would not be private and not part of the SiteBox project. --DONE, but will revisit later, when there is a config system as part of the app.

Make it work correctly with Unicode (e.g. óóóóó) characters in the Markdown source. --DONE

Make the "Delete page" button work. --DONE

Maybe indicate external links. Font Awesome's `fa-external-link` (this character: <i class='fa fa-external-link'></i>) would work. --DONE

Make literal URLs in the source be interpreted as links, e.g. source of `http://www.reddit.com/` should become [http://www.reddit.com/](http://www.reddit.com/) -- DONE: like this <http://www.reddit.com/>

## Later

Package as an open source project (see [Open Sourcing a Python Project the Right Way](http://www.jeffknupp.com/blog/2013/08/16/open-sourcing-a-python-project-the-right-way/)).

Add version control to pages on sitebox wikis (perhaps use Git?)

Allow editing a section of a page, as well as a whole page.

Make the table of contents look nicer: (i) only include sections from `##` downwards (ii) add numbering for sections, as on main part of article.

Markdown doesn't have a syntax to indent a paragraph. Add one. Note that indentation is a separate concept from blockquoting.

Do something about differently-capitalised versions of the same article e.g. `[[Python.]]` versus `[[python.]]`.

## Unresolved issues

ATM you can have a page and a subdirectory with the same name. Is this potentially confusing/unintuitive? For example if you have a page `/foo/bar` then while folder `/foo/` exists, article `/foo` might well not exist. Where there is both an article and a folder under it, maybe they should be merged. Also there is the issue with `/foo/home` which might also serve the purpose of being a top-level article for foo.

* One way to resolve this might be to deprecate pages such as `/foo/home` and just use `/foo` for the home page. If a page `/xyz` exists and there is also an `/xyz/` directory then the page might have a home icon (<i class='fa fa-home'></i>) to the right of it in the location bar to indicate this. Also, at the end of the page might be a horizontal rule followed by a list of subpages and subfolders and a link to `/xyz/`.

Remove pain points that arise when using SiteBox to document SiteBox (this will enable dogfooding). These are:

* Whether the title of a page should be determined by its URL (as with MediaWiki) or separate (as currently with SiteBox)
* Should page identifiers/titles have to begin with a capital? ATM we have some pages with the identifier "Home" and some with "home".

