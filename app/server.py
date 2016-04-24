# server.py = run the web server, using Tornado

"""
For running CatWiki using Tornado
"""


from tornado import wsgi
from tornado import httpserver, ioloop
import main
import config

if __name__ == "__main__":
    container = wsgi.WSGIContainer(main.app)
    http_server = httpserver.HTTPServer(container)
    http_server.listen(config.PORT)
    ioloop.IOLoop.instance().start()

#end
