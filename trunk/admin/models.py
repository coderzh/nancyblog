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
from google.appengine.ext import db

class Settings(db.Model):
    name = db.StringProperty()
    value = db.TextProperty()

    @staticmethod
    def get_value(name, default_value = None):
        return_value = Settings.all().filter('name =', name).get()
        if not return_value:
            new_item = Settings(name = name, value = default_value)
            new_item.put()
            return default_value
        return return_value.value


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