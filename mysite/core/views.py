from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import EmptyPage, Paginator, PageNotAnInteger
from django.core import serializers
from django.utils import formats
from django.http import JsonResponse, HttpResponse,  HttpResponseRedirect
from django.template import loader
from django.db import transaction, IntegrityError
from django.db.models import Q, Count
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.urls import reverse
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.models import Group
from django.db.models.functions import TruncMonth
from smtplib import SMTPException
from django.db.models import Sum
from django.core.management import call_command

import json
import csv
import smtplib
import ssl
import secrets
import hashlib

from datetime import datetime, date, timedelta

from django.conf import settings
from email.message import EmailMessage

from django.http import HttpResponse
# from mysite.forms import RequisitionForm
# from mysite.core.models import Company, Division, PositionGrade, Country, CandidateChannel, ChannelName, Reason, Status, Priority, Requisition, Holiday, QuarterDetail

from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email import encoders
import smtplib
import datetime as datetime
import icalendar
import pytz
from time import strftime, gmtime

from mysite.settings import BASE_DIR

import pandas as pd
import os

def SKUHealthStopLight(request):
    chartSeries = []
    connectivityChartData = []
    accuracyChartData = []
    AvailabilityChartData = []
    DQISeriesData = []

    dashboard_name = 'SKU Health Stop Light'
    
    file_path = os.path.join(BASE_DIR, 'data/Data.xlsx')
    df = pd.read_excel(file_path)
    df['Region'] = df['Region'].fillna('NA')

    runDateFilterData = df['RunDate'].unique()

    if request.method == 'POST':
        runDate = request.POST.get('runDate')
        if runDate is not None:
            radialBar_df = df[df['RunDate'] == runDate]
            data = radialBar_df.to_dict('index')
        else:
            radialBar_df = df[df['RunDate'] == '2022-03-09']
            data = radialBar_df.to_dict('index')

        region = request.POST.get('region')
        if region is not None:
            lineChart_df = df[df['Region'] == region]
            lineChartDatas = lineChart_df.to_dict('index')
        else:
            lineChart_df = df[df['Region'] == 'GLOBAL']
            lineChartDatas = lineChart_df.to_dict('index')
    else:
        radialBar_df = df[df['RunDate'] == '2022-03-09']
        data = radialBar_df.to_dict('index')

        lineChart_df = df[df['Region'] == 'GLOBAL']
        lineChartDatas = lineChart_df.to_dict('index')

    for key, value in lineChartDatas.items():
        chartSeries.append(datetime.datetime.strptime(str(value['RunDate']), "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d"))
        connectivityChartData.append(round(value['Connectivity'] * 100 , 2))
        accuracyChartData.append(round(value['Accuracy'] * 100 , 2))
        AvailabilityChartData.append(round(value['Availability'] * 100 , 2))
        DQISeriesData.append(round(value['DQI_Regional'] * 100 , 2))

    if request.is_ajax():
        return JsonResponse({
            'data': data,
            'chartSeries': chartSeries,
            'connectivityChartData': connectivityChartData,
            'accuracyChartData': accuracyChartData,
            'AvailabilityChartData': AvailabilityChartData,
            'DQISeriesData': DQISeriesData
        })
    else:                
        return render(request, 'SKUHealthStopLight.html', {
            'data': data,
            'runDateFilterData':runDateFilterData,
            'chartSeries': chartSeries,
            'connectivityChartData': connectivityChartData,
            'accuracyChartData': accuracyChartData,
            'AvailabilityChartData': AvailabilityChartData,
            'DQISeriesData': DQISeriesData,
            'dashboard_name':dashboard_name
        })

def SKUHealthLandingPageExecutive(request):
    dashboard_name = 'SKU Health Landing Page (Executive)'
    file_path = os.path.join(BASE_DIR, 'data/regional_dahsboard_data.xlsx')
    stop_light_df = pd.read_excel(file_path, sheet_name=['STOP LIGHT'])

    stop_light_df['STOP LIGHT']['Region'] = stop_light_df['STOP LIGHT']['Region'].fillna('NA')

    regionList = stop_light_df['STOP LIGHT']['Region'].unique()
    
    if request.method == 'POST':
        region = request.POST.get('region')
    else:
        region = 'GO'

    self_care_df = stop_light_df['STOP LIGHT'][(stop_light_df['STOP LIGHT']['Franchise'] == 'Self Care') & (stop_light_df['STOP LIGHT']['SKU Health Status'] == region)]
    self_care_data = self_care_df.to_dict('index')

    skin_health_df = stop_light_df['STOP LIGHT'][(stop_light_df['STOP LIGHT']['Franchise'] == 'Skin Health') & (stop_light_df['STOP LIGHT']['SKU Health Status'] == region)]
    skin_health_data = skin_health_df.to_dict('index')

    essential_health_df = stop_light_df['STOP LIGHT'][(stop_light_df['STOP LIGHT']['Franchise'] == 'Essential Health') & (stop_light_df['STOP LIGHT']['SKU Health Status'] == region)]
    essential_health_data = essential_health_df.to_dict('index')

    if request.is_ajax():
        return JsonResponse({
            'self_care_data' : self_care_data,
            'skin_health_data' : skin_health_data,
            'essential_health_data' : essential_health_data
        })
    else:
        return render(request, 'SKUHealthLandingPageExecutive.html',{
            'regionList' : regionList,
            'self_care_data' : self_care_data,
            'skin_health_data' : skin_health_data,
            'essential_health_data' : essential_health_data,
            'dashboard_name':dashboard_name
        })

def DQIRegionalSnapshot(request):
    chartSeries = []
    barChartData = []
    lineChartData = []
    file_path = os.path.join(BASE_DIR, 'data/regional_dahsboard_data.xlsx')
    df = pd.read_excel(file_path, sheet_name=['Trend Regional Snapshot'])

    dashboard_name = 'DQI Regional Snapshot'

    yearOfIssue = df['Trend Regional Snapshot']['Month, Year of Issue Date'].unique()
    for value in yearOfIssue:
        chartSeries.append(datetime.datetime.strptime(str(value), "%Y-%m-%d %H:%M:%S").strftime("%b-%Y"))

    tot_doc_field_tested_df = df['Trend Regional Snapshot'][df['Trend Regional Snapshot']['Measure Names'] == 'Tot Doc Field Tested']
    barChartDatas = tot_doc_field_tested_df.to_dict('index')
    for key, value in barChartDatas.items():
        barChartData.append(int(value['Tot Doc Field Tested']))

    accuracy_df = df['Trend Regional Snapshot'][df['Trend Regional Snapshot']['Measure Names'] == 'Accuracy %']
    lineChartDatas = accuracy_df.to_dict('index')
    for key, value in lineChartDatas.items():
        lineChartData.append(round(value['Tot Doc Field Passed %'] * 100 , 0))

    top_20_df = pd.read_excel(file_path, sheet_name=['TOP 20'])
    top_20_data = top_20_df['TOP 20'].to_dict('index')

    bottom_20_df = pd.read_excel(file_path, sheet_name=['Bottom 20'])
    bottom_20_data = bottom_20_df['Bottom 20'].to_dict('index')

    stop_light_df = pd.read_excel(file_path, sheet_name=['STOP LIGHT'])
    stop_light_df['STOP LIGHT']['Region'] = stop_light_df['STOP LIGHT']['Region'].fillna('NA')

    if request.method == 'POST':
        region = request.POST.get('region')
    else:
        region = 'GLOBAL'

    franchies_go_df = stop_light_df['STOP LIGHT'][(stop_light_df['STOP LIGHT']['Region'] == region) & (stop_light_df['STOP LIGHT']['SKU Health Status'] == 'GO')]
    franchies_go_data = franchies_go_df.to_dict('index')    

    go_grand_total = sum(franchies_go_df['Mat_Count'])

    franchies_caution_df = stop_light_df['STOP LIGHT'][(stop_light_df['STOP LIGHT']['Region'] == region) & (stop_light_df['STOP LIGHT']['SKU Health Status'] == 'CAUTION')]
    franchies_caution_data = franchies_caution_df.to_dict('index')

    caution_grand_total = sum(franchies_caution_df['Mat_Count'])

    franchies_stop_df = stop_light_df['STOP LIGHT'][(stop_light_df['STOP LIGHT']['Region'] == region) & (stop_light_df['STOP LIGHT']['SKU Health Status'] == 'STOP')]
    franchies_stop_data = franchies_stop_df.to_dict('index')

    stop_grand_total = sum(franchies_stop_df['Mat_Count'])

    region_df = stop_light_df['STOP LIGHT'][stop_light_df['STOP LIGHT']['Region'] == region]
    total = sum(region_df['Mat_Count'])

    go_percentage_of_total = (go_grand_total * 100) / total
    caution_percentage_of_total = (caution_grand_total * 100) / total
    stop_percentage_of_total = (stop_grand_total * 100) / total

    if request.is_ajax():
        return JsonResponse({
            'chartSeries' : chartSeries,
            'lineChartData': lineChartData,
            'barChartData': barChartData,
            'top_20_data': top_20_data,
            'bottom_20_data': bottom_20_data,
            'franchies_go_data': franchies_go_data,
            'go_grand_total': go_grand_total,
            'caution_grand_total': caution_grand_total,
            'stop_grand_total': stop_grand_total,
            'go_percentage_of_total' : round(go_percentage_of_total,2),
            'caution_percentage_of_total' : round(caution_percentage_of_total,2),
            'stop_percentage_of_total' : round(stop_percentage_of_total,2)
        })
    else:
        return render(request, 'DQIRegionalSnapshot.html',{
            'chartSeries' : chartSeries,
            'lineChartData': lineChartData,
            'barChartData': barChartData,
            'top_20_data': top_20_data,
            'bottom_20_data': bottom_20_data,
            'franchies_go_data': franchies_go_data,
            'go_grand_total': go_grand_total,
            'caution_grand_total': caution_grand_total,
            'stop_grand_total': stop_grand_total,
            'go_percentage_of_total' : round(go_percentage_of_total,2),
            'caution_percentage_of_total' : round(caution_percentage_of_total,2),
            'stop_percentage_of_total' : round(stop_percentage_of_total,2),
            'dashboard_name':dashboard_name
        })

def SKUHealthStopLightPage(request):
    chartSeries = []
    percentageGOEHChartData = []
    countGOEHChartData = []
    percentageGOSCChartData = []
    countGOSCChartData = []
    percentageGOSHChartData = []
    countGOSHChartData = []

    dashboard_name = 'SKU Health Stop Light Page'
   
    file_path = os.path.join(BASE_DIR, 'data/regional_dahsboard_data.xlsx')
    stop_light_df = pd.read_excel(file_path, sheet_name=['STOP LIGHT'])

    stop_light_df['STOP LIGHT']['Region'] = stop_light_df['STOP LIGHT']['Region'].fillna('NA')

    regionList = stop_light_df['STOP LIGHT']['Region'].unique()

    data_file_path = os.path.join(BASE_DIR, 'data/Data_For_SKU_and_RFT.xlsx')
    sku_trend_data_df = pd.read_excel(data_file_path, sheet_name=['SKU Trend Data'])
    lineChartDatas = sku_trend_data_df['SKU Trend Data'].to_dict('index')

    for key, value in lineChartDatas.items():
        chartSeries.append(datetime.datetime.strptime(str(value['RunDate']), "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d"))
        percentageGOEHChartData.append(round(value['Percetage GO_EH'] * 100 , 2))
        countGOEHChartData.append(round(value['EH Count'] * 100 , 2))
        percentageGOSCChartData.append(round(value['Percentage GO_SC'] * 100 , 2))
        countGOSCChartData.append(round(value['SC Count'] * 100 , 2))
        percentageGOSHChartData.append(round(value['Percentage GO_SH'] * 100 , 2))
        countGOSHChartData.append(round(value['SH Count'] * 100 , 2))

    return render(request, 'SKUHealthStopLightPage.html',{
        'regionList':regionList,
        'chartSeries':chartSeries,
        'percentageGOEHChartData':percentageGOEHChartData,
        'countGOEHChartData':countGOEHChartData,
        'percentageGOSCChartData':percentageGOSCChartData,
        'countGOSCChartData':countGOSCChartData,
        'percentageGOSHChartData':percentageGOSHChartData,
        'countGOSHChartData':countGOSHChartData,
        'dashboard_name':dashboard_name
    })

def productLevelRFTDashboard(request):
    chartSeries = []
    barChartData = []
    lineChartData = []

    franchies_go_chart = []
    franchies_caution_chart = []
    franchies_stop_chart = []

    franchies_go_chart1 = []
    franchies_caution_chart1 = []
    franchies_stop_chart1 = []

    flag=''

    dashboard_name = 'Product Level RFT Dashboard'

    data_file_path = os.path.join(BASE_DIR, 'data/Data_For_SKU_and_RFT.xlsx')
    rft_bar_chart_data_df = pd.read_excel(data_file_path, sheet_name=['RFT Bar and Trend'])
    chartDatas = rft_bar_chart_data_df['RFT Bar and Trend'].to_dict('index')        

    for key, value in chartDatas.items():
        chartSeries.append(datetime.datetime.strptime(str(value['Month of FST_SLS_DT']), "%Y-%m-%d %H:%M:%S").strftime("%b-%Y"))
        barChartData.append(int(value['Distinct count of Revised GCPH Count ']))
        lineChartData.append(round(value['Percentage of Total -  Go'] * 100 , 0))

    # ------------------------------------------

    franchisedata_df = pd.read_excel(data_file_path, sheet_name=['Franchise Bars 1'])

    franchies_go = franchisedata_df['Franchise Bars 1'][franchisedata_df['Franchise Bars 1']['Fld Lvl SKU Health'] == 'GO']

    if request.method == 'POST':
        flag = request.POST.get('flag')
    else:
        flag = 'false'

    franchies_go_data = franchies_go.to_dict('index')
    for key, value in franchies_go_data.items():
        if flag == 'false':
            franchies_go_chart.append(int(value['Count']))
        else:
            franchies_go_chart.append(round(value['Percentage'],2))
    
    franchies_caution = franchisedata_df['Franchise Bars 1'][franchisedata_df['Franchise Bars 1']['Fld Lvl SKU Health'] == 'CAUTION']
    franchies_caution_data = franchies_caution.to_dict('index')
    for key, value in franchies_caution_data.items():
        if flag == 'false':
            franchies_caution_chart.append(int(value['Count']))
        else:
            franchies_caution_chart.append(round(value['Percentage'],2))

    franchies_stop = franchisedata_df['Franchise Bars 1'][franchisedata_df['Franchise Bars 1']['Fld Lvl SKU Health'] == 'STOP']
    franchies_stop_data = franchies_stop.to_dict('index')
    for key, value in franchies_stop_data.items():
        if flag == 'false':
            franchies_stop_chart.append(int(value['Count']))
        else:
            franchies_stop_chart.append(round(value['Percentage'],2))

    # ------------------------------------------

    bpg_df = pd.read_excel(data_file_path, sheet_name=['Franchise Bars 2'])

    franchies_go = bpg_df['Franchise Bars 2'][bpg_df['Franchise Bars 2']['Fld Lvl SKU Health'] == 'GO']
    franchies_go_data = franchies_go.to_dict('index')
    for key, value in franchies_go_data.items():
        franchies_go_chart1.append(int(value['Count']))
    
    franchies_caution = bpg_df['Franchise Bars 2'][bpg_df['Franchise Bars 2']['Fld Lvl SKU Health'] == 'CAUTION']
    franchies_caution_data = franchies_caution.to_dict('index')
    for key, value in franchies_caution_data.items():
        franchies_caution_chart1.append(int(value['Count']))

    franchies_stop = bpg_df['Franchise Bars 2'][bpg_df['Franchise Bars 2']['Fld Lvl SKU Health'] == 'STOP']
    franchies_stop_data = franchies_stop.to_dict('index')
    for key, value in franchies_stop_data.items():
        franchies_stop_chart1.append(int(value['Count']))

    # table data ----------------------------

    data_file_path = os.path.join(BASE_DIR, 'data/Top_Bottom_Brand.xlsx')
    top_table_df = pd.read_excel(data_file_path, sheet_name=['Top'])
    top_table_data = top_table_df['Top'].to_dict('index')    

    bottom_table_df = pd.read_excel(data_file_path, sheet_name=['Bottom'])
    bottom_table_data = bottom_table_df['Bottom'].to_dict('index')

    if request.is_ajax():
        return JsonResponse({
            'franchies_go_chart':franchies_go_chart,
            'franchies_caution_chart':franchies_caution_chart,
            'franchies_stop_chart':franchies_stop_chart,
        })
    else:
        return render(request, 'productLevelRFTDashboard.html', {
            'chartSeries':chartSeries,
            'barChartData':barChartData,
            'lineChartData':lineChartData,
            'franchies_go_chart':franchies_go_chart,
            'franchies_caution_chart':franchies_caution_chart,
            'franchies_stop_chart':franchies_stop_chart,
            'franchies_go_chart1':franchies_go_chart1,
            'franchies_caution_chart1':franchies_caution_chart1,
            'franchies_stop_chart1':franchies_stop_chart1,
            'dashboard_name':dashboard_name,
            'top_table_data' :top_table_data,
            'bottom_table_data':bottom_table_data
        })

def home(request):
    dashboard_name = 'Vcreatek Consulting Services'
    return render(request, 'home.html',{
        'dashboard_name':dashboard_name
    })