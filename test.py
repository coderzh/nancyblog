#!/usr/bin/env python
#coding:utf-8
# Author:  CoderZh
# Purpose: Test File
# Created: 2009-11-22

from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.ext.webapp.util import run_wsgi_app

from admin.models import *
from blog.models import Blog,BlogComment

class MainPage(webapp.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        blog = Blog(title='Test Title',
                    content='Whatever Conetent',
                    tags=['Python'],
                    url = db.Link('http://localhost:8080/firstpost'))
        blog.put()
        
        comment = BlogComment(content='Good', user=users.get_current_user(), blog=blog)
        comment.put()
        
        blogs = Blog.get_blogs()
        comments = blogs[0].get_comments()
        
        theme = Settings.all().filter('name =', 'theme').get()
        if not theme:
            theme = Settings(name='theme', value='default')
            theme.put()
        
        self.response.out.write('%s\r\n%s' % (blog.title, blog.content))
        self.response.out.write('\r\nBlogs Count %d' % len(blogs))
        self.response.out.write('\r\n%s' % theme.value)

application = webapp.WSGIApplication(
    [('/test', MainPage)],
    debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()