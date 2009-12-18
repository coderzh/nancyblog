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
from blog.models import *
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
		logout_url = users.create_logout_url(self.request.uri)
		login_url = users.create_login_url(self.request.uri)
		
		values = { 'bloginfo' : BlogInfo(),
			   'stat' : Stat(),
			   'tags' : Tag.get_all(),
			   'categories' : Category.get_all_visible_categories(),
			   'archives' : Archive.get_all(),
			   'friendlists' : Friendlinks.get_top_10(),
			   'user' :  current_user,
			   'lastposts' : Blog.get_last_10(),
			   'lastcomments' : BlogComment.get_last_10(),
			   'is_admin' : is_admin,
			   'logout_url' : logout_url,
			   'login_url' : login_url,
			   }
		values.update(template_values)
		self.response.out.write(template.render(template_path, values, debug=DEBUG).decode('utf-8') )
		
class Pager:		
	def __init__(self, base_url, current_page, per_page):
		self.base_url = base_url
		if not current_page:
			self.index = 1
		else:
			try:
				self.index = int(current_page)
			except:
				self.index = 1
		self.per_page = int(per_page)
		self.first = 1
		
	def bind_datahandler(self, items_count, datahandler, *handler_args):
		self.items_count = items_count
		self.count = self.items_count / self.per_page
		if self.items_count % self.per_page != 0 or self.count == 0:
			self.count = self.count + 1
		
		self.last = self.count
		self.besidelinks = self._get_besidelinks(self.index, self.count)
		self.items = datahandler(self.per_page, self.index, *handler_args)
		
	def bind_model(self, model_class, orderby=None, *filters):
		self.items_count = get_records_count(self._get_query(model_class.all(keys_only=True), None, *filters))
		self.count = self.items_count / self.per_page
		if self.items_count % self.per_page != 0 or self.count == 0:
			self.count = self.count + 1
		
		self.last = self.count
		self.besidelinks = self._get_besidelinks(self.index, self.count)
		self.items = self._get_items(self.per_page, self.index, model_class, orderby, *filters)

	def _get_query(self, query, orderby, *filters):
		for filter in filters:
			if len(filter) < 2:
				continue
			query = query.filter(filter[0], filter[1])
		if orderby:
			query = query.order(orderby)
		return query
	
	def _get_besidelinks(self, index, count, numbers = 5):
		start = index - numbers if index - numbers > 0 else 1
		end = index + numbers if index + numbers <= count else count
		return range(start, end + 1)
	
	def _get_items(self, per_page, page_index, model_class, orderby, *filters):
		items = self._get_query(model_class.all(), orderby, *filters).fetch(per_page, (page_index - 1)*per_page)
		if not items:
			items = []
		return items
