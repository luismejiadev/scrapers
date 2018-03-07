from django.urls import path, include
from .views import get_resources, get_events
from django.views.generic import TemplateView

urlpatterns = [
    path('2018/talks/', TemplateView.as_view(template_name='fullcalendar/index.html')),
    path('2018/talks/api/events/', get_events),
    path('2018/talks/api/resources/', get_resources),
]
