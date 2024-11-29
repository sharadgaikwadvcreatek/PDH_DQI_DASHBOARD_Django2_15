from django.contrib import admin
from django.urls import path, include
from django.conf.urls import url
from django.conf import settings
from django.conf.urls.static import static

from mysite.core import views

urlpatterns = [
	url(r'^$',views.home, name='home'),
    url(r'^SKUHealthStopLight/$',views.SKUHealthStopLight, name='SKUHealthStopLight'),
    url(r'^SKUHealthLandingPageExecutive/$',views.SKUHealthLandingPageExecutive, name='SKUHealthLandingPageExecutive'),
    url(r'^DQIRegionalSnapshot/$',views.DQIRegionalSnapshot, name='DQIRegionalSnapshot'),
    url(r'^SKUHealthStopLightPage/$',views.SKUHealthStopLightPage, name='SKUHealthStopLightPage'),
    url(r'^productLevelRFTDashboard/$',views.productLevelRFTDashboard, name='productLevelRFTDashboard'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)