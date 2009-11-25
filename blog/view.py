#!/usr/bin/env python
#coding:utf-8
#
# Copyright 2009 CoderZh.com.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

__author__ = 'CoderZh'

import time
import common.authorized as authorized
from google.appengine.ext.webapp import template

from common.view import BaseRequestHandler
from blog.models import *

class MainPage(BaseRequestHandler):
    def get(self):
        self.check_login()
        blogs = Blog.get_blogs()
        template_values = {
            'blogs': blogs,
            }
        self.template_render('index.html', template_values)
        
class ViewBlog(BaseRequestHandler):
    def get(self, year, month, day, permalink):
        blog = Blog.all().filter('permalink =', permalink).get()
        template_values = { 'blog': blog}
        self.template_render('blog/view.html', template_values)
        
class YearArchive(BaseRequestHandler):
    def get(self, year):
        template_values = {}
        self.template_render('blog/year.html', template_values)
        
class MonthArchive(BaseRequestHandler):
    def get(self, year):
        template_values = {}
        self.template_render('blog/month.html', template_values)
        
class AddBlog(BaseRequestHandler):
    @authorized.role('admin')
    def get(self):
        template_values = {}
        self.template_render('blog/add.html', template_values)
    
    @authorized.role('admin')
    def post(self):
        title = self.request.POST.get('title_input')
        content = self.request.POST.get('text_input')
        permalink = self.request.POST.get('permalink')
        tags = self.request.POST.get('tags').split()
        new_blog = Blog(permalink=permalink, title=title, content=content, tags=tags)
        new_blog.put()
        
        if not new_blog.permalink:
            new_blog.permalink = str(new_blog.key())
            new_blog.put()
        self.redirect(new_blog.url())