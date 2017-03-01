# Multiple Wikis

CatWiki allows multiple wikis (aka sites) per installation, with each individual wiki being
stored in its own directory (which can have subdirectories).

The *catwiki* wiki exists by default and contains documentation and help pages for CatWiki
itself.

Other wikis are stored under `~/siteboxdata/sites/` so a wiki called **foo** would go in the
directory `~/siteboxdata/sites/foo/`.

To create a new wiki, just make a directory for it under `~/siteboxdata/sites/`.

## View all sites

The URL <http://127.0.0.1:7331/_allSites> lists all the wikis in a CatWiki installation.
