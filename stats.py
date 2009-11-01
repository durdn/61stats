#!/usr/bin/env python
#
# Copyright 2009 Nicola Paolucci
#

import logging
import os.path
import tornado.auth
import tornado.escape
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.httpclient
import uimodules
import simplejson
import socket

from tornado.options import define, options

import backend

define("port", default=8610, help="run on the given port", type=int)
define("facebook_api_key", help="your Facebook application API key",
       default="9e2ada1b462142c4dfcc8e894ea1e37c")
define("facebook_secret", help="your Facebook application secret",
       default="32fc6114554e3c53d5952594510021e2")


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", HomeHandler),
            (r"/collect/(\w+)/(\d+)", CollectHandler),
            (r"/user/(\w+)", StatsHandler),
        ]
        settings = dict(
            cookie_secret="12oETzKXQAGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo=",
            login_url="/auth/login",
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            xsrf_cookies=True,
            facebook_api_key=options.facebook_api_key,
            facebook_secret=options.facebook_secret,
            ui_modules= {"Bump": BumpModule},
            debug=False,
            server_name='61stats.durdn.com'#socket.getfqdn()
        )
        tornado.web.Application.__init__(self, handlers, **settings)


class BaseHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        user_json = self.get_secure_cookie("user")
        if not user_json: return None
        return tornado.escape.json_decode(user_json)

class CollectHandler(tornado.web.RequestHandler):
    def get(self, username,page):
        try:
            songdata,bumpdata,numpages = backend.get_song_data(username,page=page)
        except IOError,ConnectionError:
            json = {'result' : 'KO','message': 'network connection problem'};
            logging.error(str(json))
            self.write(json)
            self.finish()
            return

        backend.store_song_data(username,songdata,bumpdata)
        #numpages = 10 
        #import time;time.sleep(0.5)
        json = {'result' : 'OK','username' : username, 'page' : page, 'numpages' : numpages}
        logging.error(str(json))
        self.write(json)
        self.finish()


class StatsHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self, username):
        http = tornado.httpclient.AsyncHTTPClient()
        stats = backend.rep_sort(username)
        self.render('stats.html',stats=stats, username=username)

class HomeHandler(BaseHandler):
    def get(self):
        self.render("index.html")

class BumpModule(tornado.web.UIModule):
    def render(self, bump):
        return self.render_string("modules/bump.html", bump=bump)


def main():
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()
