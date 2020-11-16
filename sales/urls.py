from django.contrib import admin
from django.urls import path,include
from . import views

urlpatterns = [
    path('',views.main, name="Main sales page"),
    path('table/',views.salesTable, name="Sales Table"),
    path('profit/',views.calculateProfit, name="Calculates the profit for a user"),
    path('remove/',views.removeItem, name="Removes the item from the sold item db"),


]