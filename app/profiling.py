# profiling.py = profiling wiki.py

import cProfile

import wiki

#---------------------------------------------------------------------

def renderPage(siteName, pathName):
    """ render a page """
    h = wiki.wikiPage(siteName, pathName)
    print "Rendering %s %s => %d chars" % (siteName, pathName, len(h))

# render the index for softpedia:
cProfile.run('renderPage("softpedia", "")')

# end
