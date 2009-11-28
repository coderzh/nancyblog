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

from blog.models import Category
import common.authorized as authorized
from common.view import BaseRequestHandler

class MainPage(BaseRequestHandler):
    @authorized.role('admin')
    def get(self):
        self.template_render('admin/default.html')

class CategoryList(BaseRequestHandler):
    @authorized.role('admin')
    def get(self):
        categories = Category.get_all()
        tempalte_values = { 'categories' : categories }
        self.template_render('admin/categorylist.html', tempalte_values)

class AddCategory(BaseRequestHandler):
    @authorized.role('admin')
    def post(self):
        category_name = self.request.POST.get('category_name')
        category_description = self.request.POST.get('category_description')
        category_visible = self.request.POST.get('category_visible')
        
        new_category = Category(name=category_name, description=category_description, visible=category_visible == u'on')
        new_category.put()
    
        self.redirect('/admin/categorylist')

class EditCategory(BaseRequestHandler):
    @authorized.role('admin')
    def get(self):
        pass