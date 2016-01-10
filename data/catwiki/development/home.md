# Development documentation for SiteBox

* [To-do list](todo)
* [[long term development plan]]

## Data directories

These are:

* under `./data/` for SiteBox's internal wiki (the *SiteBox SiteBox*), where `./` means the top application directory.
* under `~/siteboxdata/sites/` for all wikis that aren't themselves part of the SiteBox project.

## URLs

* /{site}/w/{path} = view a wiki page or directory
* /{site}/wikiedit/{path} = view a wiki page or directory
* /_allSites = list all sites on this SiteBox installation
* /{site}/info = information about a site

## Wiki conventions

In any site or site subdirectory, `home` is the home page of that site/directory. (So the filename would be `home.md`).

In any directory, `contents` (file `contents.md`) lists the pages (and subdirectories) of that directory in order. This is used when making a printed book (or ebook, etc). 
