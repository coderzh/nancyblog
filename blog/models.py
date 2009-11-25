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

from google.appengine.api import users
from google.appengine.ext import db

class Category(db.Model):
	name = db.StringProperty()
	description = db.TextProperty()
	
class Blog(db.Model):
	permalink = db.StringProperty()
	title = db.StringProperty()
	content = db.TextProperty()
	publishdate = db.DateTimeProperty(auto_now_add=True)
	lastmodifytime = db.DateTimeProperty()
	tags = db.StringListProperty()
	#category = db.ReferenceProperty(Category)
	draft = db.BooleanProperty(default=False)
	disabled = db.BooleanProperty(default=False)
	
	@staticmethod
	def get_blogs(per_page=20, page=0):
		query = Blog.all()
		query.filter('draft =', False)
		query.filter('disabled =', False)
		query.order('-publishdate')
		return query.fetch(per_page, offset=(page*per_page))
	
	def get_comments(self, per_page=30, page=0):
		query = BlogComment.all()
		query.filter('blog =', self)
		return query.fetch(per_page, offset=(page*per_page))
	
	def url(self):
		return '/archive/%s/%s' % (self.publishdate.strftime('%Y/%m/%d'), self.permalink)
	
class BlogComment(db.Model):
	content = db.TextProperty()
	user = db.UserProperty()
	blog = db.ReferenceProperty(Blog)