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
from google.appengine.api import users
from google.appengine.api import memcache

from common.models import BaseModel

class Category(BaseModel):
	name = db.StringProperty()
	description = db.TextProperty()
	visible = db.BooleanProperty(default=True)
	
	@staticmethod
	def get_all(per_page=30, page=0):
		return Category().all().fetch(per_page, offset=(page*per_page))
	
	@staticmethod
	def get_all_visible_categories(per_page=30, page=0):
		return Category().all().filter('visible =', True).fetch(per_page, offset=(page*per_page))
	
	@staticmethod
	def delete_by_id(category_id):
		category = Category.get_by_id(int(category_id))
		blogcategories = BlogCategory.all().filter('category =', category).fetch(1000)
		while blogcategories:
			db.delete(blogcategories)
			blogcategories = BlogCategory.all().filter('category =', category).fetch(1000)
		
		category.delete()
	
class Blog(BaseModel):
	permalink = db.StringProperty()
	title = db.StringProperty()
	content = db.TextProperty()
	publishdate = db.DateTimeProperty(auto_now_add=True)
	lastmodifytime = db.DateTimeProperty()
	tags = db.StringListProperty()
	category = db.ReferenceProperty(Category)
	draft = db.BooleanProperty(default=False)
	disabled = db.BooleanProperty(default=False)
	viewcount = db.IntegerProperty(default=0)
	
	@staticmethod
	def get_blogs(per_page=20, page=0):
		query = Blog.all()
		query.filter('draft =', False)
		query.filter('disabled =', False)
		query.order('-publishdate')
		return query.fetch(per_page, offset=(page*per_page))
	
	def comments(self, per_page=30, page=0):
		query = BlogComment.all()
		query.filter('blog =', self)
		return query.fetch(per_page, offset=(page*per_page))
	
	@property
	def url(self):
		return '/archive/%s/%s' % (self.publishdate.strftime('%Y/%m/%d'), self.permalink)
	
	@property
	def comments_count(self):
		key = '%s_comments_count' % self.permalink
		count = memcache.get(key)
		if count is None:
			count = BlogComment.all().filter('blog =', self).count()
			memcache.add(key, count)
		return count
		
	@property
	def edit_url(self):
		return '/admin/editblog?id=%s' % self.key().id()
	
	@property
	def delete_url(self):
		return '/admin/deleteblog?id=%s' % self.key().id()
	
	@property
	def tags_string(self):
		return ' '.join(self.tags)
	
	def categories(self, per_page=3, page=0):
		key = '%s_categorys_%d_%d' % (self.permalink, per_page, page)
		value = memcache.get(key)
		if value is None:
			blogcategories = BlogCategory.all().filter('blog =', self).fetch(per_page, offset=(page*per_page))
			value = []
			for blogcategory in blogcategories:
				try:
					value.append(blogcategory.category)
				except:
					blogcategory.delete()
			if value:
				memcache.add(key, value)
		return value
	
	@staticmethod
	def delete_by_id(blog_id):
		blog = Blog.get_by_id(int(blog_id))
		blogcategories = BlogCategory.all().filter('blog =', blog).fetch(1000)
		while blogcategories:
			db.delete(blogcategories)
			blogcategories = BlogCategory.all().filter('blog =', blog).fetch(1000)
		
		blog.delete()
	
class BlogComment(BaseModel):
	content = db.TextProperty()
	user = db.UserProperty()
	blog = db.ReferenceProperty(Blog)
	
class BlogCategory(BaseModel):
	blog = db.ReferenceProperty(Blog)
	category = db.ReferenceProperty(Category)
	
class Pager:
	def __init__(self, model_class, current_index, numbers_per_page):
		self.model_class = model_class
		self.index = current_index
		self.numbers_per_page = int(numbers_per_page)
		
		self.items_count = model_class.count_all()
		self.count = self.items_count / self.numbers_per_page
		if self.items_count % self.numbers_per_page != 0 or self.count == 0:
			self.count = self.count + 1
		
		self.first = 1
		self.last = self.count
		self.besidelinks = self._get_besidelinks(self.index, self.count)
		self.items = self._get_items(self.numbers_per_page, self.index)

	def _get_besidelinks(self, index, count, numbers = 5):
		start = index - numbers if index - numbers > 0 else 1
		end = index + numbers if index + numbers <= count else count
		return range(start, end + 1)
	
	def _get_items(self, numbers_per_page, page_index):
		items = self.model_class.all().fetch(numbers_per_page, page_index)
		if not items:
			items = []
		return items
		