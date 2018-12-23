"""ChargeFee URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from apps.management.views import index, login_view, logout_view, ChargeListView, QueryListView, SummaryListView, charges


urlpatterns = [
    path('', ChargeListView.as_view(), name='charge'),
    path('admin/', admin.site.urls, name='admin'),
    path('index.html', index, name='index'),
    path('login.html', login_view, name='login'),
    path('logout.html', logout_view, name='logout'),
    path('charge.html', ChargeListView.as_view(), name='charge'),
    path('query.html', QueryListView.as_view(), name='query'),
    path('summary.html', SummaryListView.as_view(), name='summary'),
    path('charges', charges, name='charges'),
]
