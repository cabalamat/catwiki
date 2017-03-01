# Installing CatWiki

Instructions to install CatWiki.

## Prerequisites

You must have Python 2.7 and Git installed on your system.

## Download

Download the software using `git`:

    $ git clone git@github.com:cabalamat/catwiki.git

Go into the new directory:

    $ cd catwiki

Set up a virtual environment:

    $ virtualenv venv
    $ . venv/bin/activate

Use `pip` to download the dependencies:

    $ pip install -r requirements.txt

## Run the software

Now you can either run the software using the Tornado web server, for production. Or for development you can use the Flask web server.

### Run with production web server

    $ cd app
    $ python server.py

### Run with development web server

    $ cd app
    $ python main.py

## Use the software

Now point your web browser to <http://127.0.0.1:7331/>. This will display [all the wikis](multiple wikis)
in your installation.
