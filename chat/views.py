from rest_framework import  generics, permissions

from chat.models import Message
from chat.serializers import MessageSerializer


class MessageView(generics.ListCreateAPIView):
    serializer_class = MessageSerializer
    permission_classes = [permissions.AllowAny]
    queryset = Message.objects.all()


class MessageDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = MessageSerializer
    permission_classes = [permissions.AllowAny]
    queryset = Message.objects.all()
