# Goals of MeowCat

[TOC]

## Three original concepts

The ideas around [MeowCat](home) stemmed from what were originally three separate ideas for projects in my mind:

* **Concept 1 -- ???**: Anti-censorship software that would enable secure private communication and anonymous public communication (this concept I called **MeowCat**)

* **Concept 2 -- ????**: A "website in a box" site (hence the name **SiteBox**) containing a blog, a wiki, and other tools that a group of people who want to communicate/collaborate on the internet might want. Think of it as [Wordpress](https://wordpress.com/) but with a built-in wiki.

* **Concept 3** (no name): A platform for writing books and technical documentation, ideally collaboratively. Think of a web-based front-end to [Pandoc](http://johnmacfarlane.net/pandoc/) coupled with an intuitive user interface to [Git](http://git-scm.com/) and [Github](https://github.com/)-like functionality. [GitBook](https://www.gitbook.io/) is a project along these lines. *"Github for writers"* might be a good slogan for this part of the project.

 - - - -

## Putting them together

The more I thought about these ideas, the more I realised there was considerable overlap between them.

Concepts 1 and 2 both need a system where people can post messages, reply to others and have threaded conversations. Concepts 3 would also benefit from this as an aid to collaboration.

Concepts 2 and 3 both include wikis. Concept 1 would benefit from wiki-like functionality.

Put together Concept 1 and Concept 3, and you have people collaboratively writing books in secret, without having to meet face to face or knowing each others' identities.

## Goals in detail

The three concepts I've listed above are somewhat vague in detail. To flesh them out, I've detailed various [use-cases](MeowCat Use-Cases).

## Implementation

This is a big project that can't be done all at once. So it will be done in stages.

### Stage 1: dogfood

The first stage is to get the project good enough to be self-hosting, i.e. so I can document the SiteBox project in itself.

### Open sourcing

The project will be published on GitHub. I'll use the checklist in [open-sourcing a Python project the right way](http://www.jeffknupp.com/blog/2013/08/16/open-sourcing-a-python-project-the-right-way/).

### Deploying it to my meowc.at server

Once the software is ready I will deploy it to my server at `meowc.at`.

This will serve two purposes:

1. people will be able to use it to create their own websites/wikis

2. it will contain the documentation for SiteBox
