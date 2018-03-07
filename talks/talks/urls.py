from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('pycon/', include('fullcalendar.urls'))
]
