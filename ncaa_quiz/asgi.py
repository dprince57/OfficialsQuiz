# ncaa_quiz/asgi.py
import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ncaa_quiz.settings')

application = get_asgi_application()
