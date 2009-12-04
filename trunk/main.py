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

def main():
    application = webapp.WSGIApplication([
        ('/*$', blog.view.MainPage),
        #('/images/(.*)', blog.view.ImagesHandler),
        #('/stylesheets/(.*)', blog.view.StyleSheetsHandler),
        #('/page/(\d*)/*$', blog.PageHandle),
        #('/403.html', blog.UnauthorizedHandler),
        #('/404.html', blog.NotFoundHandler),
        
        ('/archive/([12]\d\d\d)/(\d|[01]\d)/(\d|[0123]\d)/([-\w]+)/*$', blog.view.ViewBlog),
        ('/archive/([12]\d\d\d)/*$', blog.view.YearArchive),
        ('/archive/([12]\d\d\d)/(\d|[01]\d)/*$', blog.view.MonthArchive),
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
        #('/search/(.*)/*$', blog.SearchHandler),
        #('/tag/(.*)', blog.TagHandler),
        #('/delicious/(.*)', blog.DeliciousHandler),
        #('/atom/*$', blog.FeedHandler),
        #('/sitemap/*$', blog.SiteMapHandler),
    ], debug = DEBUG)
    
    wsgiref.handlers.CGIHandler().run(application)

    
if __name__ == '__main__':
    main()