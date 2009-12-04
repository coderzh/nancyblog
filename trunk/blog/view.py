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

import common.fckeditor as fckeditor
import common.authorized as authorized
from common.captcha import *
from common.config import DisplayInfo
from common.view import BaseRequestHandler, Pager
from blog.models import *
from admin.models import Settings

class MainPage(BaseRequestHandler):
    def get(self):
        blogs = Blog.get_blogs()
        template_values = {
            'blogs': blogs,
            }
        self.template_render('default.html', template_values)
                
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
        
        new_blog = Blog(permalink=permalink, title=title, content=content, tags=tags)
        new_blog.put()
        
        if not new_blog.permalink:
            new_blog.permalink = str(new_blog.key())
            new_blog.put()

        categories = Category.get_all_visible_categories(1000)
        for category in categories:
            if self.request.POST.get('category_%s' % category.key().id()) is not None:
                new_blogcategory = BlogCategory(blog=new_blog, category=category)
                new_blogcategory.put()
        
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
        tags = self.request.POST.get('tags').split()
        
        blog = Blog.get_by_id(int(blog_id))
        if blog:
            blog.title = title
            blog.content = content
            if permalink:
                blog.permalink = permalink
            blog.tags = tags
            blog.put()
        else:
            blog = Blog(title=title, content=content, permalink=permalink, tags=tags)
            blog.put()
            if not permalink:
                blog.permalink = str(blog.key())
                blog.put()
        
        categories = Category.get_all_visible_categories(1000)
        for category in categories:
            if self.request.POST.get('category_%s' % category.key().id()) is not None:
                alreadyexits = BlogCategory.all().filter('blog =', blog).filter('category =', category).count()
                if not alreadyexits:
                    new_blogcategory = BlogCategory(blog=blog, category=category)
                    new_blogcategory.put()
        
        self.redirect(blog.url)
        

class ViewBlog(BaseRequestHandler):
    def get(self, year, month, day, permalink):
        blog = Blog.all().filter('permalink =', permalink).get()
        captcha = displayhtml('6LdMwQkAAAAAAPcIdSaDTkhqsrQxO-5f5WkrLorI')
        template_values = { 'blog': blog, 'reCAPTCHA' : captcha }
        self.template_render('viewblog.html', template_values)

class DeleteBlog(BaseRequestHandler):
    @authorized.role('admin')
    def get(self):
        blog_id = self.request.GET.get('id')
        if blog_id:
            Blog.delete_by_id(blog_id)
        self.redirect('/admin/bloglist')

class BlogList(BaseRequestHandler):
    @authorized.role('admin')
    def get(self):
        page_index = self.request.GET.get('page')
        if not page_index:
            page_index = 1
        else:
            try:
                page_index = int(page_index)
            except:
                page_index = 1
                
        pager = Pager('/admin/bloglist', page_index, DisplayInfo().admin_pages, Blog)
        
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
    
            blog = Blog.get_by_id(int(blog_id))
            
            if (not valifation_result.is_valid) or (not blog):
                self.response.out.write('0')
                return
                    
            new_comment = BlogComment(username=name, content=comment, blog=blog)
            if email:
                new_comment.email = email
            if url:
                new_comment.userlink = url
            new_comment.put()
            
            blog.increase_comments_count()
            
            self.response.out.write('1')
        except:
            self.response.out.write('-1')
            
class DeleteComment(BaseRequestHandler):
    @authorized.role('admin')
    def get(self):
        comment_id = self.request.GET.get('id')
        try:
            comment = BlogComment.get_by_id(int(comment_id))
            if comment:
                blog = comment.blog
                comment.delete()
                blog.decrese_comments_count()
                self.redirect(blog.url)
            else:
                self.redirect('/')
        except:
            self.redirect('/')
            
class EditComment(BaseRequestHandler):
    @authorized.role('admin')
    def get(self):
        pass