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

import os
import time
import datetime
import cgi
import common.fckeditor as fckeditor
import common.authorized as authorized
from common.captcha import *
from common.config import DisplayInfo
from common.view import BaseRequestHandler, Pager
from blog.models import *
from admin.models import Settings

from google.appengine.api import urlfetch,memcache

class MainPage(BaseRequestHandler):
    def get(self):
        key_home = 'home'
        #cache_home = memcache.get(key_home)
        
        #if cache_home is not None:
        #    self.response.out.write(cache_home)
        #    return
        page_index = self.request.GET.get('page')                
        pager = Pager('/', page_index, DisplayInfo().blog_pages)
        pager.bind_datahandler(Blog.get_published_blogs_count(), Blog.get_published_blogs)
        
        template_values = { 
            'page' : pager,
        }
        self.template_render('default.html', template_values)
        
        #cache_home = self.response.out.getvalue()
        #memcache.add(key_home, cache_home)
                
class YearArchive(BaseRequestHandler):
    def get(self, year):
        template_values = {}
        self.template_render('blog/year.html', template_values)
        
class MonthArchive(BaseRequestHandler):
    def get(self, yearmonth):
        page_index = self.request.GET.get('page')                
        pager = Pager('/archive/%s' % yearmonth, page_index, DisplayInfo().blog_pages)
        pager.bind_datahandler(Archive.get_yearmonth_count(yearmonth),
                               Blog.get_blogs_by_yearmonth,
                               yearmonth)
        
        template_values = { 'page' : pager }
        self.template_render('viewlist.html', template_values)
        
class AddBlog(BaseRequestHandler):
    @authorized.role('admin')
    def get(self):        
        oFCKeditor = fckeditor.FCKeditor('text_input')
        oFCKeditor.Height = 500
        oFCKeditor.BasePath = '/fckeditor/'

        fckeditor_html = oFCKeditor.Create()

        template_values = { 'categories' : Category.get_all_visible_categories(1000),
                            'fckeditor' : fckeditor_html}
        
        self.template_render('admin/addblog.html', template_values)
    
    @authorized.role('admin')
    def post(self):
        title = self.request.POST.get('title_input')
        content = self.request.POST.get('text_input')
        permalink = self.request.POST.get('permalink')
        tags = self.request.POST.get('tags').split()
        
        new_blog = Blog.create_blog(permalink, title, content, tags)
        
        categories = Category.get_all_visible_categories()
        for category in categories:
            if self.request.POST.get('category_%s' % category.key().id()) is not None:
                BlogCategory.create_blogcategory(new_blog, category)
        
        self.redirect(new_blog.url)
        
class EditBlog(BaseRequestHandler):
    @authorized.role('admin')
    def get(self):
        blog_id = self.request.GET.get('id')
        blog = Blog.get_by_id(int(blog_id))
        
        oFCKeditor = fckeditor.FCKeditor('text_input')
        oFCKeditor.Height = 500
        oFCKeditor.BasePath = '/fckeditor/'
        oFCKeditor.Value = blog.content
        
        fckeditor_html = oFCKeditor.Create()
        template_values = { 'blog' : blog, 'categories' : Category.get_all_visible_categories(1000),
                            'fckeditor' : fckeditor_html}
        self.template_render('admin/editblog.html', template_values)
    
    @authorized.role('admin')
    def post(self):
        blog_id = self.request.POST.get('id')
        title = self.request.POST.get('title_input')
        content = self.request.POST.get('text_input')
        permalink = self.request.POST.get('permalink')
        tags = self.request.POST.get('tags')
        
        blog = Blog.update_blog(blog_id, permalink, title, content, tags)
        
        categories = Category.get_all_visible_categories()
        for category in categories:
            blogcategory = BlogCategory.all().filter('blog =', blog).filter('category =', category).get()
            if self.request.POST.get('category_%s' % category.key().id()) is not None:
                if not blogcategory:
                    BlogCategory.create_blogcategory(blog, category)
            else:
                if blogcategory:
                    BlogCategory.delete_blogcategory(blogcategory)
        
        self.redirect(blog.url)
        

class ViewBlog(BaseRequestHandler):
    def get(self, year, month, day, permalink):
        blog = Blog.all().filter('permalink =', permalink).get()
        captcha = displayhtml('6LdMwQkAAAAAAPcIdSaDTkhqsrQxO-5f5WkrLorI')
        template_values = { 
            'blog': blog,
            'reCAPTCHA' : captcha,
        }
        self.template_render('viewblog.html', template_values)

class DeleteBlog(BaseRequestHandler):
    @authorized.role('admin')
    def get(self):
        blog_id = self.request.GET.get('id')
        if blog_id:
            Blog.delete_blog(blog_id)
        self.redirect('/admin/bloglist')

class BlogList(BaseRequestHandler):
    @authorized.role('admin')
    def get(self):
        page_index = self.request.GET.get('page')                
        pager = Pager('/admin/bloglist', page_index, DisplayInfo().admin_pages)
        pager.bind_model(Blog)
        
        template_values = { 'page' : pager }
        self.template_render('admin/bloglist.html', template_values)
        
class AddComment(BaseRequestHandler):
    def post(self):
        self.response.headers['Content-Type'] = 'text/plain'
        try:            
            blog_id = self.request.POST.get('blog_id')
            name = self.request.POST.get('name')
            comment = self.request.POST.get('comment')
            url = self.request.POST.get('url')
            email = self.request.POST.get('email')
    
            comment = comment.replace('\n', '<br />')
            recaptcha_challenge_field = self.request.POST.get('recaptcha_challenge_field')
            recaptcha_response_field = self.request.POST.get('recaptcha_response_field')
            valifation_result = submit(recaptcha_challenge_field, recaptcha_response_field,'6LdMwQkAAAAAALf6TyLYGIZyuWdDM0CItskn7Ck3', self.request.remote_addr)
              
            if not valifation_result.is_valid:
                self.response.out.write('0')
                return
                    
            BlogComment.create_comment(name, email, url, comment, blog_id)
            
            self.response.out.write('1')
        except:
            self.response.out.write('-1')
            
class DeleteComment(BaseRequestHandler):
    @authorized.role('admin')
    def get(self):
        comment_id = self.request.GET.get('id')
        blog = BlogComment.delete_comment(comment_id)
        self.redirect(blog.url)
            
class EditComment(BaseRequestHandler):
    @authorized.role('admin')
    def get(self):
        pass
    
class ViewTag(BaseRequestHandler):
    def get(self, tag_name):
        tag_name = urllib.unquote(tag_name).decode('utf-8')
        page_index = self.request.GET.get('page')                
        pager = Pager('/tag/%s' % tag_name, page_index, DisplayInfo().tag_pages)
        pager.bind_datahandler(Tag.get_tag(tag_name).blogs_count,
                               Blog.get_blogs_by_tag,
                               tag_name)
        
        template_values = { 'page' : pager }
        self.template_render('viewlist.html', template_values)
        
class ViewCategory(BaseRequestHandler):
    def get(self, category_name):
        category_name = urllib.unquote(category_name).decode('utf-8')
        page_index = self.request.GET.get('page')
        pager = Pager('/category/%s' % category_name, page_index, DisplayInfo().tag_pages)
        pager.bind_datahandler(Category.get_blogs_count(category_name),
                               Blog.get_blogs_by_category,
                               category_name)
        
        template_values = { 'page' : pager }
        self.template_render('viewlist.html', template_values)
        
class FeedHandler(BaseRequestHandler):
    def get(self):
        blogs = Blog.get_last_10()
        last_updated = datetime.datetime.now()
        if blogs and blogs[0]:
            last_updated = blogs[0].publishdate
            last_updated = last_updated.strftime("%Y-%m-%dT%H:%M:%SZ")
        for blog in blogs:
            blog.formatted_date = blog.publishdate.strftime("%Y-%m-%dT%H:%M:%SZ")
        self.response.headers['Content-Type'] = 'application/atom+xml'
        template_values = { 'blogs' : blogs}
        self.template_render('atom.xml', template_values)