from django.conf.urls import url, include
from . import views

urlpatterns = [
    url(r'^$', views.Home.IndexView.as_view(), name='index'),
    url(r'^compression/$', views.Home.AppView.as_view(), name='app'),
    url(r'^ecg_chart/$', views.Home.ECGChartAjaxView.as_view(), name='ecg_chart')
]
