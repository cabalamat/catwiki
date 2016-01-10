# Redirection

MediaWiki does redirects by having a page `foo` containing 

```
#REDIRECT [ [bar] ]
```

This means that when a user follows a link `[[foo]]` they are redirected to `[[bar]]` and the system says they've been redirected.

In SiteBox, `#` is a special character (at the start of a line it puts text in an `<h1>` tag), so it may make sense to use another character, for example `!`:

    !REDIRECT [bar]

In English text, "!" is rarely immediately followed by a alphabetic character, so this combination would be a good one for SiteBox special codes.