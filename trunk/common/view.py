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
from admin.models import *
import common.config as config

from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template

class BaseRequestHandler(webapp.RequestHandler):
	def template_render(self, template_name, template_values={}):
		theme = Settings.get_value(config.Theme_Name, config.Theme_DefaultValue)
		directory = os.path.split(os.path.dirname(__file__))[0]
		template_path = os.path.join(directory, config.Theme_Folder, theme, template_name)
		
		values = { 'bloginfo' : BlogInfo() }
		values.update(template_values)
		self.response.out.write(template.render(template_path, values, debug=config.Debug))