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

class BlogInfo(object):
    __shared_values = {}
    def __init__(self):
        if not BlogInfo.__shared_values:
            offset = 0
            settings = Settings.all().fetch(20, offset)
            count = len(settings)
            
            if count == 0:
                self.init_settings()
            else:
                while True:
                    for setting in settings:
                        BlogInfo.__shared_values[setting.name] = setting.value

                    if count < 20:
                        break;
                
                    offset += 20
                    settings = Settings.all().fetch(20, offset)
                    count = len(settings)
                            
        self.__dict__ = BlogInfo.__shared_values

    def init_settings(self):
        init_values = { 
            'author' : ('CoderZh', u'博客作者名称'),
            'email' : ('coderzh@gmail.com', u'博客作者名称'),
            'homepage' : ('http://blog.coderzh.com', u'作者主页'),
            'blogtitle' : ('Nancy Blog', u'博客标题'),
            'subtitle' : ('This is NancyBlog', u'子标题'),
            'theme' : ('default', u'博客皮肤'),
            'announce' : (u'欢迎使用NancyBlog', u'公告'),
            'admin_pages' : ('20', u'管理页面每页显示条数'),
            'blog_pages' : ('20', u'首页博客每页显示条数'),
            'comment_pages' : ('50', u'评论每页显示条数'),
            'tag_pages' : ('50', u'Tag每页显示条数'),
            'rss_coderzh' : ('http://feeds.feedburner.com/coderzh', u'rss地址'),
            'rss_coderzh_description' : (u'我的技术博客', u'rss描述'),
        }
        
        for name, value in init_values.items():
            setting = Settings(name=name, value=value[0], description=value[1])
            setting.put()
            BlogInfo.__shared_values[name] = value[0]
            
    @staticmethod
    def delete_setting(id):
        setting_item = Settings.get_by_id(int(id))
        if setting_item:
            key = 'setting_%s' % setting_item.name
            setting_item.delete()
            BlogInfo.__shared_values.pop(setting_item.name)
            
    @staticmethod
    def update_setting(id, name, value, description):
        setting_item = Settings.get_by_id(int(id))
        if setting_item:
            if setting_item.name != name:
                BlogInfo.__shared_values.pop(setting_item.name)
                setting_item.name = name
            setting_item.value = value
            setting_item.description = description
            setting_item.put()
            BlogInfo.__shared_values[name] = value
