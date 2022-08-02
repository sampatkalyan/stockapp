from django.urls import path
from .views import *

urlpatterns = [
    path('',stockSelector,name="stockpicker"),
    path('stocktracker/',stocktracker,name="stocktracker"),
]