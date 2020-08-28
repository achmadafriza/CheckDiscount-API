from django.contrib import admin
from django.urls import path, include
import api.views as views

app_name = 'api'

urlpatterns = [
    path('checktransaction', views.checkDiscount, name="checkDiscount"),
]