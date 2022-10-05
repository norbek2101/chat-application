from django.urls import path
from chat.consumers import ChatConsumer


websocket_urlpatterns = [
    path('chat/', ChatConsumer.as_asgi()),
]