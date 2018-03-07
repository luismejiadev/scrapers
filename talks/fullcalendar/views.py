import json
from django.shortcuts import render
from django.views.generic import TemplateView
from django.http import HttpResponse, Http404
from .utils import *

COLORS = [
    'blue',
    'green',
    'red',
    'orange',
    'brown',
]


def get_resources(request):
    data = []
    for i, room in enumerate(RESOURCES.keys()):
        print(i, room)
        data.append(
            {'id': room, 'title': room, 'eventColor': COLORS[i]}
        )
    return HttpResponse(json.dumps(data), content_type="application/json", status=200)


def get_events(request):
    data = []
    for e in EVENTS:
        event = {
            'id': e['id'],
            'resourceId': RESOURCES[e['room']],
            'start': e['start_date'].strftime("%Y-%m-%dT%H:%M"),
            'end': e['end_date'].strftime("%Y-%m-%dT%H:%M"),
            'title': e['title'],
            'duration': e['duration'],
            'description': e['description'],
            'url': e['url'],
            'speakers': e['speakers'],
        }
        data.append(event)
    return HttpResponse(json.dumps(data), content_type="application/json", status=200)

