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

from admin.models import Settings
from common.config import DisplayInfo
from common.view import BaseRequestHandler, Pager
from blog.models import Category, BlogCategory

import common.authorized as authorized

class MainPage(BaseRequestHandler):
    @authorized.role('admin')
    def get(self):
        self.template_render('admin/default.html')

class CategoryList(BaseRequestHandler):
    @authorized.role('admin')
    def get(self):
        tempalte_values = {}
        editcategoryid = self.request.GET.get('editcategoryid')
        if editcategoryid:
            tempalte_values['editcategory'] = Category.get_by_id(int(editcategoryid))
            
        categories = Category.get_all()
        tempalte_values['categories'] = categories
        self.template_render('admin/categorylist.html', tempalte_values)

class AddCategory(BaseRequestHandler):
    @authorized.role('admin')
    def post(self):
        category_name = self.request.POST.get('category_name')
        category_description = self.request.POST.get('category_description')
        category_visible = self.request.POST.get('category_visible')
        edit_categoryid = self.request.POST.get('editcategoryid')

        if edit_categoryid:
            Category.update_category(edit_categoryid, category_name, category_description, category_visible == u'on')
        else:
            Category.create_category(category_name, category_description, category_visible == u'on')
    
        self.redirect('/admin/categorylist')
        
    
class DeleteCategory(BaseRequestHandler):
    @authorized.role('admin')
    def get(self):
        try:
            category_id = self.request.GET.get('id')
            Category.delete_category(category_id)
        finally:
            self.redirect('/admin/categorylist')
        
class AdvanceSettings(BaseRequestHandler):
    @authorized.role('admin')
    def get(self):
        page_index = self.request.GET.get('page')
        if not page_index:
            page_index = 1
        else:
            try:
                page_index = int(page_index)
            except:
                page_index = 1
                
        pager = Pager('/admin/advancesettings', page_index, DisplayInfo().admin_pages)
        pager.bind_model(Settings)
        
        template_values = { 'page' : pager }
        self.template_render('admin/advancesettings.html', template_values)
        
class DeleteSettings(BaseRequestHandler):
    @authorized.role('admin')
    def get(self):
        try:
            setting_id = self.request.GET.get('id')
            Settings.delete_setting(setting_id)
            self.redirect('/admin/advancesettings')
        except:
            self.error(500)
            
class EditSettings(BaseRequestHandler):
    @authorized.role('admin')
    def post(self):
        try:
            setting_id = self.request.POST.get('setting_id')
            name = self.request.POST.get('name')
            value = self.request.POST.get('value')
            description = self.request.POST.get('description')
            Settings.update_setting(setting_id, name, value, description)
            self.redirect('/admin/advancesettings')
        except:
            self.error(500)