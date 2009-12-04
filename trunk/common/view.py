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
from common.config import *
from common.models import get_records_count

from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template

class BaseRequestHandler(webapp.RequestHandler):
	def template_render(self, template_name, template_values={}):
		directory = os.path.split(os.path.dirname(__file__))[0]
		template_path = os.path.join(directory, THEMES_FOLDER, THEMES, template_name)
		
		current_user = users.get_current_user()
		is_admin = users.is_current_user_admin()
		
		values = { 'bloginfo' : BlogInfo(),
				   'user' :  current_user,
				   'is_admin' : is_admin}
		values.update(template_values)
		self.response.out.write(template.render(template_path, values, debug=DEBUG))
		
class Pager:
	def __init__(self, base_url, current_index, numbers_per_page, model_class, *filters):
		self.base_url = base_url
		self.index = current_index
		self.numbers_per_page = int(numbers_per_page)
		
		self.items_count = get_records_count(self._get_query(model_class.all(keys_only=True), *filters))
		self.count = self.items_count / self.numbers_per_page
		if self.items_count % self.numbers_per_page != 0 or self.count == 0:
			self.count = self.count + 1
		
		self.first = 1
		self.last = self.count
		self.besidelinks = self._get_besidelinks(self.index, self.count)
		self.items = self._get_items(self.numbers_per_page, self.index, model_class, *filters)

	def _get_query(self, query, *filters):
		for filter in filters:
			if len(filter) < 2:
				continue
			query = query.filter(filter[0], filter[1])
		return query
	
	def _get_besidelinks(self, index, count, numbers = 5):
		start = index - numbers if index - numbers > 0 else 1
		end = index + numbers if index + numbers <= count else count
		return range(start, end + 1)
	
	def _get_items(self, numbers_per_page, page_index, model_class, *filters):
		items = self._get_query(model_class.all(), *filters).fetch(numbers_per_page, (page_index - 1)*numbers_per_page)
		if not items:
			items = []
		return items