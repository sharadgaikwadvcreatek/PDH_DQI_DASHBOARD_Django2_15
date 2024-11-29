from __future__ import unicode_literals
from django import template
import datetime as datetime
from django.conf import settings
from django.shortcuts import render
from datetime import date
from mysite.settings import BASE_DIR
import pandas as pd
import os
import math

register = template.Library()

@register.filter('calculate_percentage')
def calculate_percentage(value):
    return round(value * 100, 2)

@register.filter('changeDateFormat')
def changeDateFormat(value):
    changeDate = datetime.datetime.strptime(str(value), "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d")
    return changeDate

@register.filter('getTotalAndPercentage')
def getTotalAndPercentage(value, sku_status):
    data = {}

    file_path = os.path.join(BASE_DIR, 'data/regional_dahsboard_data.xlsx')
    stop_light_df = pd.read_excel(file_path, sheet_name=['STOP LIGHT'])

    stop_light_df['STOP LIGHT']['Region'] = stop_light_df['STOP LIGHT']['Region'].fillna('NA')

    franchies_go_df = stop_light_df['STOP LIGHT'][(stop_light_df['STOP LIGHT']['Region'] == value) & (stop_light_df['STOP LIGHT']['SKU Health Status'] == sku_status)]

    grand_total = sum(franchies_go_df['Mat_Count'])

    region_df = stop_light_df['STOP LIGHT'][stop_light_df['STOP LIGHT']['Region'] == value]
    total = sum(region_df['Mat_Count'])
    
    if total > 0:
        percentage_of_total = (grand_total * 100) / total
    else:
        percentage_of_total = 0

    data.update({"percentage_of_total": round(percentage_of_total, 1)})
    data.update({"grand_total": round(grand_total, 1)})
    data.update({"total": round(total, 1)})

    return data

@register.filter('getTotal')
def getTotal(region, sku_status=None):
    file_path = os.path.join(BASE_DIR, 'data/regional_dahsboard_data.xlsx')
    stop_light_df = pd.read_excel(file_path, sheet_name=['STOP LIGHT'])

    stop_light_df['STOP LIGHT']['Region'] = stop_light_df['STOP LIGHT']['Region'].fillna('NA')
    
    franchies_go_df = stop_light_df['STOP LIGHT'][(stop_light_df['STOP LIGHT']['Region'] == region) & (stop_light_df['STOP LIGHT']['SKU Health Status'] == sku_status)]

    grand_total = sum(franchies_go_df['Mat_Count'])

    return grand_total

@register.filter('getPercentage')
def getPercentage(region, sku_status):
    file_path = os.path.join(BASE_DIR, 'data/regional_dahsboard_data.xlsx')
    stop_light_df = pd.read_excel(file_path, sheet_name=['STOP LIGHT'])

    stop_light_df['STOP LIGHT']['Region'] = stop_light_df['STOP LIGHT']['Region'].fillna('NA')

    franchies_go_df = stop_light_df['STOP LIGHT'][(stop_light_df['STOP LIGHT']['Region'] == region) & (stop_light_df['STOP LIGHT']['SKU Health Status'] == sku_status)]

    grand_total = sum(franchies_go_df['Mat_Count'])

    region_df = stop_light_df['STOP LIGHT'][stop_light_df['STOP LIGHT']['Region'] == region]
    total = sum(region_df['Mat_Count'])

    percentage_of_total = (grand_total * 100) / total

    return round(percentage_of_total,1)

@register.filter('getFranchiseDetail')
def getFranchiseDetail(region, sku_status):
    file_path = os.path.join(BASE_DIR, 'data/regional_dahsboard_data.xlsx')
    stop_light_df = pd.read_excel(file_path, sheet_name=['STOP LIGHT'])

    stop_light_df['STOP LIGHT']['Region'] = stop_light_df['STOP LIGHT']['Region'].fillna('NA')

    franchies_go_df = stop_light_df['STOP LIGHT'][(stop_light_df['STOP LIGHT']['Region'] == region) & (stop_light_df['STOP LIGHT']['SKU Health Status'] == sku_status)]
    franchies_go_data = franchies_go_df.to_dict('index')

    return franchies_go_data

@register.filter('get_value')
def get_value(value):
    if math.isnan(value):
        return '-'
    else:
        return round(value)

@register.filter('get_value_percentage')
def get_value_percentage(value):
    if math.isnan(value):
        return '-'
    else:
        return round(value * 100, 2)