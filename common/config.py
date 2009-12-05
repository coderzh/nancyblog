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

from admin.models import Settings

DEBUG = True

THEMES_FOLDER = 'themes'
THEMES = 'default'

class BaseInfo(object):
    def __setattr__(self, name, value):
        object.__setattr__(self, name, value)
        Settings.update_value(name, value)

class BlogInfo(BaseInfo):        
    @property
    def author(self):
        return Settings.get_value('author', 'CoderZh', u'博客作者名称')
    
    @property
    def email(self):
        return Settings.get_value('email', 'coderzh@gmail.com', u'作者邮箱')
    
    @property
    def homepage(self):
        return Settings.get_value('homepage', 'http://coderzh.cnblogs.com', u'作者主页')
    
    @property
    def blogtitle(self):
        return Settings.get_value('blogtitle', 'Nancy Blog', u'博客标题')
    
    @property
    def subtitle(self):
        return Settings.get_value('subtitle', 'This is NancyBlog', u'子标题')
    
    @property
    def theme(self):
        return Settings.get_value('theme', 'default', u'博客皮肤')
    
    @property
    def announce(self):
        return Settings.get_value('announce', u'欢迎使用NancyBlog', u'公告')
        
class DisplayInfo(BaseInfo):
        
    @property
    def admin_pages(self):
        return int(Settings.get_value('admin_pages', '20', u'管理页面每页显示条数'))
    
    @property
    def blog_pages(self):
        return int(Settings.get_value('blog_pages', '20', u'首页博客每页显示条数'))
    
    @property
    def comment_pages(self):
        return int(Settings.get_value('comment_pages', '50', u'评论每页显示条数'))
    
    @property
    def tag_pages(self):
        return int(Settings.get_value('tag_pages', '50', u'Tag每页显示条数'))