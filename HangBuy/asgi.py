"""
ASGI config for HangBuy project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/asgi/
"""

import os
import socket

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application
from django.urls import path

from app import chatter

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'HangBuy.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AllowedHostsOriginValidator(AuthMiddlewareStack(URLRouter((
        path('api/user/<int:user_id>/chat/', chatter.Chatter.as_asgi()),
        path('', chatter.Dummy.as_asgi()),  # Fix nginx related bug maybe?
    ))))
})


def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.0.0.0', 1))
        ip = s.getsockname()[0]
        s.close()
    except:
        ip = '127.0.0.1'
    print(f"Server can be accessed by {ip}")
    return ip


get_local_ip()
