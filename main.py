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

import wsgiref.handlers
from google.appengine.ext import webapp

from common.config import DEBUG
import blog.view
import admin.view
import admin.tasks

from google.appengine.ext.webapp import template
template.register_template_library('common.filter')

def main():
    application = webapp.WSGIApplication([
        ('/*$', blog.view.MainPage),
        ('/page/(.*)/*$', blog.view.PageHandle),

        ('/archive/([12]\d\d\d)/(\d|[01]\d)/(\d|[0123]\d)/([-\w]+)/*$', blog.view.ViewBlog),
        ('/archive/(\d*)/*$', blog.view.MonthArchive),
        ('/blog/addcomment/*$', blog.view.AddComment),
        ('/blog/editcomment/*$', blog.view.EditComment),
        ('/blog/deletecomment/*$', blog.view.DeleteComment),

        ('/admin/*$', blog.view.BlogList),
        ('/admin/addblog/*$', blog.view.AddBlog),
        ('/admin/editblog/*$', blog.view.EditBlog),
        ('/admin/bloglist/*$', blog.view.BlogList),
        ('/admin/deleteblog/*$', blog.view.DeleteBlog),

        ('/admin/categorylist/*$', admin.view.CategoryList),
        ('/admin/addcategory/*$', admin.view.AddCategory),
        ('/admin/deletecategory/*$', admin.view.DeleteCategory),

        ('/admin/advancesettings/*$', admin.view.AdvanceSettings),
        ('/admin/deletesettings/*$', admin.view.DeleteSettings),
        ('/admin/editsettings/*$', admin.view.EditSettings),

        ('/admin/linklist/*$', admin.view.FriendlinkList),
        ('/admin/addlink/*$', admin.view.AddFriendlink),
        ('/admin/editlink/*$', admin.view.AddFriendlink),
        ('/admin/deletelink/*$', admin.view.DeleteFriendlink),

        ('/tag/(.*)/*$', blog.view.ViewTag),
        ('/category/(.*)/*$', blog.view.ViewCategory),
        ('/rssreader/(.*)/*$', blog.view.RssReaderHandler),
        ('/atom/*$', blog.view.FeedHandler),
        ('/tasks/flushmemcache/*$', admin.tasks.FlushMemcache),
        ('/500.html', blog.view.ErrorHandler),
        ('/(.*)', blog.view.NotFoundHandler),
        ], debug = DEBUG)

    wsgiref.handlers.CGIHandler().run(application)


if __name__ == '__main__':
    main()
