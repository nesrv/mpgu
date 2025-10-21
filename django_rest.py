import os
import django
from django.conf import settings
import time
import random

# Минимальная конфигурация Django + DRF
settings.configure(
    DEBUG=True,
    SECRET_KEY='test-key',
    ROOT_URLCONF=__name__,
    ALLOWED_HOSTS=['*'],
    INSTALLED_APPS=[
        'django.contrib.contenttypes',
        'django.contrib.auth',
        'rest_framework',
    ],
    REST_FRAMEWORK={
        'DEFAULT_RENDERER_CLASSES': [
            'rest_framework.renderers.JSONRenderer',
        ]
    }
)
django.setup()

from django.urls import path
from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['GET'])
def fast_endpoint(request):
    return Response({'response': 'fast', 'latency': '10ms'})

@api_view(['GET'])
def slow_endpoint(request):
    time.sleep(random.uniform(0.1, 0.5))  # 100-500ms задержка
    return Response({'response': 'slow', 'latency': '100-500ms'})

@api_view(['GET'])
def test_api(request):
    return Response({'результаты теста': '123'})

@api_view(['GET'])
def api_root(request):
    return Response({
        'endpoints': {
            'fast': '/api/fast/',
            'slow': '/api/slow/',
            'test-api': '/api/test-api/'
        }
    })

from django.urls import include

urlpatterns = [
    path('api/', api_root),
    path('api/', include([
        path('fast/', fast_endpoint),
        path('slow/', slow_endpoint),
        path('test-api/', test_api),
    ])),
]

if __name__ == '__main__':
    from django.core.management import execute_from_command_line
    execute_from_command_line(['manage.py', 'runserver', '0.0.0.0:8002'])