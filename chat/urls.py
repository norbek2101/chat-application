from django.urls import path
from chat import views
urlpatterns = [
    path('', views.MessageView.as_view()),
    path('chat-detail/<int:pk>/', views.MessageDetailView.as_view()),
]
