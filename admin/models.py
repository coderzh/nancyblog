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

import common.config as config
from common.models import BaseModel

from google.appengine.ext import db
from google.appengine.api import memcache

class Settings(BaseModel):
    name = db.StringProperty()
    value = db.TextProperty()

    @staticmethod
    def get_value(name, default_value = None):
        setting_item = memcache.get(name)
        
        if setting_item is None:
            setting_item = Settings.all().filter('name =', name).get()
            if not setting_item:
                setting_item = Settings(name = name, value = str(default_value))
                setting_item.put()
            
            memcache.add(name, setting_item)
            
        return setting_item.value


class BlogInfo():
    _instance = None
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Singleton, cls).__new__(cls, *args, **kwargs)
        return cls._instance
    
    def __init__(self):
        self.title = Settings.get_value('blogtitle', config.BlogTitle)
        self.author = Settings.get_value('author', config.Author)
        self.homepage = Settings.get_value('homepage', config.HomePage)