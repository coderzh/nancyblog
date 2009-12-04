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

def get_records_count(query):
	count = 0
	query = query.order('__key__')

	while 1:
		current_count = query.count()
		count += current_count
		if current_count == 0:
			break

		last_key = query.fetch(1, current_count-1)[0]
		query = query.filter('__key__ > ', last_key)

	return count
	

class BaseModel(db.Model):
	@classmethod
	def count_all(cls):
		"""
		Count *all* of the rows (without maxing out at 1000)
		"""
		return get_records_count(cls.all())