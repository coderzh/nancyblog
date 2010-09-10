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
import common.feedparser as feedparser
from common.captcha import *
from common.config import BlogInfo
from common.view import BaseRequestHandler, Pager
from blog.models import *
from admin.models import Settings

from google.appengine.api import urlfetch,memcache

# for pdb debug
from common.debug import set_trace

class MainPage(BaseRequestHandler):
    def get(self):
        try:
            pager_home_key = 'pager_home'
            pager = memcache.get(pager_home_key)
            if pager is None: 
                page_index = self.request.GET.get('page')                
                pager = Pager('/', page_index, BlogInfo().blog_pages)
                pager.bind_datahandler(Blog.get_published_blogs_count_cache(), Blog.get_published_blogs)
                memcache.add(pager_home_key, pager, 60)

            template_values = { 
                'page' : pager,
            }
            self.template_render_theme('index.html', template_values)
        except:
            raise
#            self.redirect('/500.html')


class PageHandle(BaseRequestHandler):
    def get(self, page_name):
        try:
            blog = Blog.all().filter('permalink =', page_name).get()
            if not blog:
                self.redirect('/')
            else:
                captcha = displayhtml('6LdMwQkAAAAAAPcIdSaDTkhqsrQxO-5f5WkrLorI')
                template_values = { 
                    'blog': blog,
                    'reCAPTCHA' : captcha,
                }
                blog.viewcount += 1
                blog.put()
                self.template_render_theme('blog.html', template_values)
        except:
            self.redirect('/500.html')

class YearArchive(BaseRequestHandler):
    def get(self, year):
        try:
            template_values = {}
            self.template_render('blog/year.html', template_values)
        except:
            self.redirect('/500.html')

class MonthArchive(BaseRequestHandler):
    def get(self, yearmonth):
        try:
            page_index = self.request.GET.get('page')                
            pager = Pager('/archive/%s' % yearmonth, page_index, BlogInfo().blog_pages)
            pager.bind_datahandler(Archive.get_yearmonth_count(yearmonth),
                                   Blog.get_blogs_by_yearmonth,
                                   yearmonth)

            template_values = { 'page' : pager }
            self.template_render_theme('bloglist.html', template_values)
        except:
            self.redirect('/500.html')

class AddBlog(BaseRequestHandler):
    @authorized.role('admin')
    def get(self):
        try:
            entrytype = 'post'
            if 'page' == self.request.GET.get('entrytype'):
                entrytype = 'page'
            oFCKeditor = fckeditor.FCKeditor('text_input')
            oFCKeditor.Height = 500
            oFCKeditor.BasePath = '/fckeditor/'

            fckeditor_html = oFCKeditor.Create()

            template_values = { 'categories' : Category.get_all_visible_categories(1000),
                                'fckeditor' : fckeditor_html,
                                'entrytype' : entrytype}

            self.template_render('admin/addblog.html', template_values)
        except:
            self.redirect('/500.html')

    @authorized.role('admin')
    def post(self):
        try:
            title = self.request.POST.get('title_input')
            content = self.request.POST.get('text_input')
            permalink = self.request.POST.get('permalink')
            tags = self.request.POST.get('tags').split()
            draft = False
            if self.request.POST.get('submitdraft'):
                draft = True
            entrytype = self.request.POST.get('entrytype')

            new_blog = Blog.create_blog(permalink, title, content, tags, draft=draft, entrytype=entrytype)

            categories = Category.get_all_visible_categories()
            for category in categories:
                if self.request.POST.get('category_%s' % category.key().id()) is not None:
                    BlogCategory.create_blogcategory(new_blog, category)

            self.redirect(new_blog.url)
        except:
            self.redirect('/500.html')

class EditBlog(BaseRequestHandler):
    @authorized.role('admin')
    def get(self):
        try:
            blog_id = self.request.GET.get('id')
            blog = Blog.get_by_id(int(blog_id))

            oFCKeditor = fckeditor.FCKeditor('text_input')
            oFCKeditor.Height = 500
            oFCKeditor.BasePath = '/fckeditor/'
            oFCKeditor.Value = blog.content

            fckeditor_html = oFCKeditor.Create()
            template_values = { 'editblog' : blog, 'categories' : Category.get_all_visible_categories(1000),
                                'fckeditor' : fckeditor_html,
                                'entrytype' : blog.entrytype}
            self.template_render('admin/addblog.html', template_values)
        except:
            self.redirect('/500.html')

    @authorized.role('admin')
    def post(self):
        try:
            blog_id = self.request.POST.get('id')
            title = self.request.POST.get('title_input')
            content = self.request.POST.get('text_input')
            permalink = self.request.POST.get('permalink')
            tags = self.request.POST.get('tags')
            entrytype = self.request.POST.get('entrytype')
            draft = False
            if self.request.POST.get('submitdraft'):
                draft = True

            blog = Blog.update_blog(blog_id, permalink, title, content, tags, draft=draft, entrytype=entrytype)

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
        except:
            self.redirect('/500.html')


class ViewBlog(BaseRequestHandler):
    def get(self, year, month, day, permalink):
        try:
            blog = Blog.all().filter('permalink =', permalink).get()
            blog.viewcount += 1
            blog.put()
            captcha = displayhtml('6LdMwQkAAAAAAPcIdSaDTkhqsrQxO-5f5WkrLorI')
            template_values = { 
                'blog': blog,
                'reCAPTCHA' : captcha,
            }
            self.template_render_theme('blog.html', template_values)
        except:
            self.redirect('/500.html')

class DeleteBlog(BaseRequestHandler):
    @authorized.role('admin')
    def get(self):
        try:
            blog_id = self.request.GET.get('id')
            if blog_id:
                Blog.delete_blog(blog_id)
            self.redirect('/admin/bloglist')
        except:
            self.redirect('/500.html')

class BlogList(BaseRequestHandler):
    @authorized.role('admin')
    def get(self):
        try:
            blog_type = self.request.GET.get('type')
            items_count = 0
            datahandler = None
            if blog_type == 'page':
                items_count = Blog.get_pagetype_blogs_count()
                datahandler = Blog.get_pagetype_blogs
            elif blog_type == 'draft':
                items_count = Blog.get_draft_blogs_count()
                datahandler = Blog.get_draft_blogs
            else:
                items_count = Blog.get_posttype_blogs_count()
                datahandler = Blog.get_posttype_blogs

            page_index = self.request.GET.get('page')                
            pager = Pager('/admin/bloglist', page_index, BlogInfo().admin_pages)
            pager.bind_datahandler(items_count, datahandler)

            template_values = { 'page' : pager }
            self.template_render('admin/bloglist.html', template_values)
        except:
            self.redirect('/500.html')

class AddComment(BaseRequestHandler):
    def post(self):
        self.response.headers['Content-Type'] = 'text/plain'
        try:            
            blog_id = self.request.POST.get('blog_id')
            name = self.request.POST.get('name')
            comment = self.request.POST.get('comment')
            url = self.request.POST.get('url')
            email = self.request.POST.get('email')

            comment = cgi.escape(comment).replace('\n', '<br/>')
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
        try:
            comment_id = self.request.GET.get('id')
            blog = BlogComment.delete_comment(comment_id)
            self.redirect(blog.url)
        except:
            self.redirect('/500.html')

class EditComment(BaseRequestHandler):
    @authorized.role('admin')
    def get(self):
        pass

class ViewTag(BaseRequestHandler):
    def get(self, tag_name):
        try:
            tag_name = urllib.unquote(tag_name).decode('utf-8')
            page_index = self.request.GET.get('page')                
            pager = Pager('/tag/%s' % tag_name, page_index, BlogInfo().tag_pages)
            pager.bind_datahandler(Tag.get_tag(tag_name).blogs_count,
                                   Blog.get_blogs_by_tag,
                                   tag_name)

            template_values = { 'page' : pager }
            self.template_render_theme('bloglist.html', template_values)
        except:
            self.redirect('/500.html')

class ViewCategory(BaseRequestHandler):
    def get(self, category_name):
        try:
            category_name = urllib.unquote(category_name).decode('utf-8')
            page_index = self.request.GET.get('page')
            pager = Pager('/category/%s' % category_name, page_index, BlogInfo().tag_pages)
            pager.bind_datahandler(Category.get_blogs_count(category_name),
                                   Blog.get_blogs_by_category,
                                   category_name)

            template_values = { 'page' : pager }
            self.template_render_theme('bloglist.html', template_values)
        except:
            self.redirect('/500.html')

class FeedHandler(BaseRequestHandler):
    def get(self):
        blogs = Blog.get_last_10()
        last_updated = datetime.datetime.now()
        if blogs and blogs[0]:
            last_updated = blogs[0].publishtime
            last_updated = last_updated.strftime("%Y-%m-%dT%H:%M:%SZ")
        for blog in blogs:
            blog.formatted_date = blog.publishtime.strftime("%Y-%m-%dT%H:%M:%SZ")
        self.response.headers['Content-Type'] = 'application/atom+xml'
        template_values = { 
            'blogs' : blogs,
            'last_updated' : last_updated,
        }
        self.template_render('atom.xml', template_values)

class NotFoundHandler(BaseRequestHandler):
    def get(self, url):
        self.template_render('404.html', { 'url' : url })

class ErrorHandler(BaseRequestHandler):
    def get(self):
        self.template_render('500.html')

class RssReaderHandler(BaseRequestHandler):
    def get(self, feedname):
        try:
            feed_result_key = 'feed_result_%s' % feedname
            result = memcache.get(feed_result_key)
            if result is None:
                url_name = 'rss_%s' % feedname
                url = getattr(BlogInfo(), url_name, u'http://feeds.feedburner.com/coderzh')
                try_times = 0
                result = feedparser.parse(url)
                while result.bozo and try_times < 10:
                    try_times += 1
                    time.sleep(1)
                    result = feedparser.parse(url)
                description_name = 'rss_%s_description' % feedname
                result.feed['custom_description'] = getattr(BlogInfo(), description_name, u'')
                memcache.add(feed_result_key, result, 36000)

            template_values = {
                'feed' : result.feed,
                'entries' : result.entries,
            }
            self.template_render_theme('viewrss.html', template_values)
        except:
            self.redirect('/500.html')
