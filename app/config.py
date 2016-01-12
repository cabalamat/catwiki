# config.py = configuration data

import os.path
from ulib import butil

#---------------------------------------------------------------------

# port we are running on
PORT=7331

# A list of directories which might be followed by sites.
# New sites are always created using the last one on this list.
SITE_STUBS = [
     butil.join(os.path.dirname(__file__), "../data"),
     butil.join("~/siteboxdata/sites"),
]

#---------------------------------------------------------------------

#end
