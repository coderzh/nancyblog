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

from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.api import memcache

from common.models import BaseModel, get_records_count

class Category(BaseModel):
	name = db.StringProperty()
	description = db.TextProperty()
	visible = db.BooleanProperty(default=True)
		
	@staticmethod
	def get_all(per_page=30, page=1):
		return Category().all().fetch(per_page, offset=((page-1)*per_page))
	
	@staticmethod
	def get_all_visible_categories(per_page=1000, page=1):
		return Category().all().filter('visible =', True).fetch(per_page, offset=((page-1)*per_page))
	
	@staticmethod
	def delete_category(category_id):
		category = Category.get_by_id(int(category_id))
		if category:
			BlogCategory.delete_by_category(category)
			category.delete()
			
	@staticmethod
	def create_category(name, description, visible):
		new_category = Category(name = name, description = description, visible = visible)
		new_category.put()
		
	@staticmethod
	def update_category(category_id, name, description, visible):
		category = Category.get_by_id(int(category_id))
		category.name = name
		category.description = description
		category.visible = visible
		category.put()
		self.update_blogs_count()
		
	@property
	def url(self):
		return '/category/%s' % urllib.unquote(self.name.encode('utf-8'))
	
	@property
	def blogs_count(self):
		key = 'blogs_count_%s' % self.name
		count = memcache.get(key)
		if count is None:
			query = BlogCategory.all(keys_only=True).filter('category =', self)
			count = get_records_count(query)
			memcache.add(key, count)
		return count
	
	@staticmethod
	def get_blogs_count(category_name):
		key = 'blogs_count_%s' % category_name
		count = memcache.get(key)
		if count is None:
			count = 0
			category = Category.all().filter('name =', category_name).get()
			if category:
				query = BlogCategory.all(keys_only=True).filter('category =', category)
				count = get_records_count(query)
				memcache.add(key, count)
		return count
	
	def increase_blogs_count_cache(self, delta=1):
		key = 'blogs_count_%s' % self.name
		memcache.incr(key, delta)

	def decrease_blogs_count_cache(self, delta=1):
		key = 'blogs_count_%s' % self.name
		memcache.decr(key, delta)
		
	def delete_blogs_count_cache(self):
		key = 'blogs_count_%s' % self.name
		memcache.delete(key)
		
	def update_blogs_count(self):
		key = 'blogs_count_%s' % self.name
		query = BlogCategory.all(keys_only=True).filter('category =', self)
		count = get_records_count(query)
		memcache.set(key, count)
	
class Blog(BaseModel):
	permalink = db.StringProperty()
	title = db.StringProperty()
	content = db.TextProperty()
	publishdate = db.DateTimeProperty(auto_now_add=True)
	lastmodifytime = db.DateTimeProperty(auto_now=True)
	tags = db.StringListProperty()
	draft = db.BooleanProperty(default=False)
	disabled = db.BooleanProperty(default=False)
	viewcount = db.IntegerProperty(default=0)
	author = db.UserProperty(auto_current_user_add=True)
	showtop = db.BooleanProperty(default=False)
	
	
	@staticmethod
	def get_published_blogs(per_page=20, page=1):
		query = Blog.all().filter('draft =', False).filter('disabled =', False).order('-publishdate')
		return query.fetch(per_page, offset=((page-1)*per_page))
	
	@staticmethod
	def get_blogs_by_tag(per_page=20, page=1, tag=''):
		query = Blog.all().filter('draft =', False).filter('disabled =', False).filter('tags =',tag).order('-publishdate')
		return query.fetch(per_page, offset=((page-1)*per_page))
	
	@staticmethod
	def get_blogs_by_category(per_page=20, page=1, category_name=''):
		blogs = []
		category = Category.all().filter('name =', category_name).get()
		if category:
			query = BlogCategory.all().filter('category =', category)
			blogcategories = query.fetch(per_page, offset=((page-1)*per_page))
			for blogcategory in blogcategories:
				blogs.append(blogcategory.blog)
		return blogs
		
	
	@staticmethod
	def get_published_blogs_count():
		key = 'blogcount'
		count = memcache.get(key)
		if count is not None:
			return count

		query = Blog.all(keys_only=True)
		query.filter('draft =', False)
		query.filter('disabled =', False)
		count = get_records_count(query)
		memcache.add(key, count)
		return count
	
	@staticmethod
	def increase_published_blogs_count_cache(delta=1):
		memcache.incr('blogcount', delta)

	@staticmethod
	def decrease_published_blogs_count_cache(delta=1):
		memcache.decr('blogcount', delta)
		
	@staticmethod
	def create_blog(permalink, title, content, tags, draft=False, disabled=False, showtop=False):
		new_blog = Blog(permalink=permalink, title=title, content=content, tags=tags, draft=draft, showtop = showtop)
		new_blog.put()
		if not new_blog.permalink:
			new_blog.permalink = str(new_blog.key())
			new_blog.put()
		
		Blog.increase_published_blogs_count_cache()
		Tag.increase_tag_count_cache(tags)
		Tag.update_all()
		return new_blog

	@staticmethod
	def update_blog(blog_id, permalink, title, content, tags, draft=False, disabled=False, showtop=False):
		blog = Blog.get_by_id(int(blog_id))
		if blog:
			blog.title = title
			blog.content = content
			if permalink:
				blog.permalink = permalink
			old_tags = set(blog.tags)
			blog.tags = tags.split()
			new_tags = set(blog.tags)
			blog.put()
			
			# update tag stat
			delete_tags = set.difference(old_tags, new_tags)
			new_tags = set.difference(new_tags, old_tags)
			Tag.decrease_tag_count_cache(delete_tags)
			Tag.increase_tag_count_cache(new_tags)
			Tag.update_all()
			
		else:
			blog = Blog.create_blog(permalink, title, content, tags)
		return blog
		
	@staticmethod
	def delete_blog(blog_id):
		blog = Blog.get_by_id(int(blog_id))
		blogcategories = BlogCategory.all().filter('blog =', blog).fetch(1000)
		while blogcategories:
			db.delete(blogcategories)
			blogcategories = BlogCategory.all().filter('blog =', blog).fetch(1000)
		
		blog.delete()
		Blog.decrease_published_blogs_count_cache()
		Tag.decrease_tag_count_cache(blog.tags)
		Tag.update_all()
	
	def comments(self, per_page=30, page=0):
		query = BlogComment.all()
		query.filter('blog =', self)
		return query.fetch(per_page, offset=(page*per_page))
	
	@property
	def url(self):
		return '/archive/%s/%s' % (self.publishdate.strftime('%Y/%m/%d'), 
								   urllib.unquote(self.permalink.encode('utf-8')))
	
	@property
	def comments_count(self):
		key = '%s_comments_count' % self.permalink
		count = memcache.get(key)
		if count is None:
			count = BlogComment.all(keys_only=True).filter('blog =', self).count()
			memcache.add(key, count)
		return count
	
	def decrease_comments_count_cache(self, delta=1):
		key = '%s_comments_count' % self.permalink
		memcache.decr(key, delta)
	
	def increase_comments_count_cache(self, delta=1):
		key = '%s_comments_count' % self.permalink
		memcache.incr(key, delta)
		
	@property
	def edit_url(self):
		return '/admin/editblog?id=%s' % self.key().id()
	
	@property
	def delete_url(self):
		return '/admin/deleteblog?id=%s' % self.key().id()
	
	@property
	def tags_string(self):
		return ' '.join(self.tags)
	
	def categories(self, per_page=3, page=1):
		value = []
		blogcategories = BlogCategory.all().filter('blog =', self).fetch(per_page, offset=((page-1)*per_page))
			
		for blogcategory in blogcategories:
			try:
				value.append(blogcategory.category)
			except:
				blogcategory.delete()
		return value
	
	@staticmethod
	def get_all_tags():
		tags = set()
		blogcount = Blog.get_published_blogs_count()
		page = 1
		blogs = Blog.get_published_blogs(1000, page)
		
		while blogs:
			for blog in blogs:
				tags = set.union(tags, set(blog.tags))
			page += 1
			blogs = Blog.get_published_blogs(1000, page)
			
		return tags
	
class BlogComment(BaseModel):
	content = db.TextProperty()
	username = db.StringProperty()
	email = db.EmailProperty()
	userlink = db.LinkProperty()
	blog = db.ReferenceProperty(Blog)
	time = db.DateTimeProperty(auto_now=True)

	@classmethod
	def get_comments_count(cls):
		key = 'comments_count'
		count = memcache.get(key)
		if count is None:
			count = cls.count_all()
			memcache.add(key, count)
		return count
	
	@staticmethod
	def increase_comments_count(delta=1):
		memcache.incr('comments_count', delta)
		
	@staticmethod
	def decrease_comments_count(delta=1):
		memcache.decr('comments_count', delta)
	
class BlogCategory(BaseModel):
	blog = db.ReferenceProperty(Blog)
	category = db.ReferenceProperty(Category)
	
	@staticmethod
	def create_blogcategory(blog, category):
		new_blogcategory = BlogCategory(blog=blog, category=category)
		new_blogcategory.put()
		# update cache
		category.increase_blogs_count_cache()
		
	@staticmethod
	def delete_by_category(category):
		category.delete_blogs_count_cache()
		blogcategories = BlogCategory.all().filter('category =', category).fetch(1000)
		while blogcategories:
			db.delete(blogcategories)
			blogcategories = BlogCategory.all().filter('category =', category).fetch(1000)
		
	@staticmethod
	def delete_blogcategory(blogcategory):
		blogcategory.category.decrease_blogs_count_cache()
		blogcategory.delete()
	
class Tag:
	def __init__(self, name, blogs_count):
		self.name = name
		self.blogs_count = blogs_count
		self.url = '/tag/%s' % urllib.unquote(name.encode('utf-8'))
	
	@staticmethod
	def get_tag(name):
		key = 'tag_%s' % name
		count = memcache.get(key)
		if count is None:
			query = Blog.all(keys_only=True).filter('tags =', name)
			count = get_records_count(query)
			memcache.add(key, count)
		return Tag(name, count)
	
	@staticmethod
	def increase_tag_count_cache(tag_names):
		for tag_name in tag_names:
			key = 'tag_%s' % tag_name
			memcache.incr(key)
	
	@staticmethod
	def decrease_tag_count_cache(tag_names):
		for tag_name in tag_names:
			key = 'tag_%s' % tag_name
			memcache.decr(key)
				
	@staticmethod
	def get_all():
		key = 'alltag'
		tags = memcache.get(key)
		if tags is None:
			tags = []
			tagnames = Blog.get_all_tags()
			for name in tagnames:
				tags.append(Tag.get_tag(name))
			memcache.add(key, tags)
		return tags
	
	@staticmethod
	def update_all():
		tags = []
		tagnames = Blog.get_all_tags()
		for name in tagnames:
			tags.append(Tag.get_tag(name))

		memcache.set('alltag', tags)
	
class Stat:
	@property
	def blogs_count(self):
		return Blog.get_published_blogs_count()
	
	@property
	def comments_count(self):
		return BlogComment.get_comments_count()