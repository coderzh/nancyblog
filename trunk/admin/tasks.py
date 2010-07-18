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

from google.appengine.ext import db
from google.appengine.api import memcache
from google.appengine.ext import webapp
import common.authorized as authorized

class FlushMemcache(webapp.RequestHandler):
    @authorized.role('admin')
    def get(self):
        try:
            memcache.flush_all()
            self.response.out.write('ok')
        except:
            self.redirect('/500.html')