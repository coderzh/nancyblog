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

import urllib
from common.models import BaseModel

from google.appengine.ext import db
from google.appengine.api import memcache

class Settings(BaseModel):
    name = db.StringProperty()
    value = db.TextProperty()
    description = db.TextProperty()

    @staticmethod
    def get_value(name, default_value = None, default_description = None):
        key = 'setting_%s' % name
        setting_item = memcache.get(key)
        if setting_item is None:
            setting_item = Settings.all().filter('name =', name).get()
            if not setting_item:
                setting_item = Settings(name = name, value = unicode(default_value), description = unicode(default_description))
                setting_item.put()
            memcache.add(key, setting_item)
            
        return setting_item.value
    
    @staticmethod
    def update_value(name, value):
        setting_item = Settings.all().filter('name =', name).get()
        if not setting_item:
            return
        
        setting_item.value = db.Text(value)
        setting_item.put()
            
        key = 'setting_%s' % name
        value = memcache.get(key)
        if value is not None:
            memcache.set(key, setting_item)
        else:
            memcache.add(key, setting_item)
    
    @staticmethod
    def delete_setting(id):
        setting_item = Settings.get_by_id(int(id))
        if setting_item:
            key = 'setting_%s' % setting_item.name
            memcache.delete(key)
            setting_item.delete()
            
    @staticmethod
    def update_setting(id, name, value, description):
        setting_item = Settings.get_by_id(int(id))
        if setting_item:
            key = 'setting_%s' % setting_item.name
            setting_item.name = name
            setting_item.value = value
            setting_item.description = description
            setting_item.put()
            
            value = memcache.get(key)
            if value is not None:
                memcache.set(key, setting_item)
            else:
                memcache.add(key, setting_item)
           
    @property
    def edit_url(self):
        return '/admin/editsettings?id=%s' % self.key().id()
    
    @property
    def delete_url(self):
        return '/admin/deletesettings?id=%s' % self.key().id()

#class Menus(BaseModel):
 #   text = db.StringProperty()
  #  url = db.StringProperty()
    
class Friendlinks(BaseModel):
    title = db.StringProperty()
    url = db.URLProperty()
    description = db.TextProperty()
    
    @staticmethod
    def get_top_10():
        return Friendlinks.all().fetch(10)
    
    @staticmethod
    def create_link(title, url, description):
        new_link = Friendlinks(title=title, url=url, description=description)
        new_link.put()
        
    @staticmethod
    def delete_link(link_id):
        delete_link = Friendlinks.get_by_id(int(link_id))
        if delete_link:
            delete_link.delete()
        
    @staticmethod
    def update_link(link_id, title, url, description):
        edit_link = Friendlinks.get_by_id(int(link_id))
        if edit_link:
            edit_link.title = title
            edit_link.url = url
            edit_link.description = description
            edit_link.put()
    
    @property
    def delete_url(self):
        return '/admin/deletelink?id=%s' % self.key().id()
    
    @property
    def edit_url(self):
        return '/admin/linklist?editlinkid=%s' % self.key().id()
