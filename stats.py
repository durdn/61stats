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

define("port", default=8888, help="run on the given port", type=int)
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
            debug=True,
            server_name='localhost:8888'#socket.getfqdn()
        )
        tornado.web.Application.__init__(self, handlers, **settings)


class BaseHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        user_json = self.get_secure_cookie("user")
        if not user_json: return None
        return tornado.escape.json_decode(user_json)

class CollectHandler(tornado.web.RequestHandler):
    def get(self, username,page):
        songdata,bumpdata,numpages = backend.get_song_data(username,page=page)
        backend.store_song_data(username,songdata,bumpdata)
        logging.error(simplejson.dumps(('OK',int(page),numpages)))
        return self.write(simplejson.dumps(('OK',username,int(page),numpages)))


class StatsHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self, username):
        http = tornado.httpclient.AsyncHTTPClient()
        if self.get_argument("reload", None):
            self.page = 1
            http.fetch("http://%s/collect/%s/1" % (self.settings['server_name'],username), callback=self.async_callback(self.on_response))
        else:
            stats = backend.rep_sort(username)
            self.render('stats.html',stats=stats)

    def on_response(self, response):
        http = tornado.httpclient.AsyncHTTPClient()
        if response.error: 
            logging.error('error:%s' % response.error)
            raise tornado.web.HTTPError(500)
        json = tornado.escape.json_decode(response.body)
        logging.error('received response %s' % simplejson.dumps(json))
        if json[0] == 'OK':
            self.username = json[1]
            self.page = int(json[2])
            self.numpages = int(json[3])
            self.write(simplejson.dumps(('OK',self.page,self.numpages)))
            if self.page == self.numpages - 1:
                self.finish()
                self.page = 0
                self.numpages = 0
                self.username = ''
                return
            else:
                self.page = self.page + 1
                logging.error('new request %s' % simplejson.dumps(('OK',int(self.page),self.numpages)))
                http.fetch("http://%s/collect/%s/%d" % (self.settings['server_name'],self.username,self.page), callback=self.async_callback(self.on_response))
                return
        logging.error('closing long poll')
        self.page = 0
        self.numpages = 0
        self.username = ''
        self.finish()

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
