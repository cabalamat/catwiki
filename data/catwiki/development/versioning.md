# Versioning

It would be very useful if the site could track old versions of pages, like Wikipedia can.

One way to do this would be to use a MongoDB database, with a collection `pageVersion` with these fields:

* `_id` = needed by MongoDB

These form a composite primary key:

* `site` = the name of the site it is part of
* `wikiAddress` = this is the address within the wiki (a partial URL such as `development/versioning`)
* `hash` = a hash of the contents
* `timestamp` = timestamp of version in as a string in format `"yyyymmddhhmmss"`. Yes MongoDB has its own date format but it's a PITA

Other fields:

* `contents` = the contents of the page

