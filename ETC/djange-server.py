import os
import django
from django.conf import settings
from django.http import JsonResponse
from django.urls import path
from django.core.wsgi import get_wsgi_application
import time
import random

# Минимальная конфигурация Django
settings.configure(
    DEBUG=True,
    SECRET_KEY='test-key',
    ROOT_URLCONF=__name__,
    ALLOWED_HOSTS=['*'],
)
django.setup()

def fast_endpoint(request):
    return JsonResponse({'response': 'fast', 'latency': '10ms'})

def slow_endpoint(request):
    time.sleep(random.uniform(0.1, 0.5))  # 100-500ms задержка
    return JsonResponse({'response': 'slow', 'latency': '100-500ms'})

urlpatterns = [
    path('fast/', fast_endpoint),
    path('slow/', slow_endpoint),
]

if __name__ == '__main__':
    from django.core.management import execute_from_command_line
    execute_from_command_line(['manage.py', 'runserver', '0.0.0.0:8001'])