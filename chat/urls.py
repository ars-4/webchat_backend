from django.urls import re_path, path, include
from . import views
from .consumer import ChatConsumer
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('persons', views.PersonViewSet, basename='persons')
router.register('notes', views.NoteViewSet, basename='notes')

websocket_urlpatterns = [
    re_path(r"ws/chats/(?P<room_name>\w+)/$", ChatConsumer.as_asgi()),
]

urlpatterns = [

    path('', views.index),
    path('login/', views.login),
    path('validate_token/', views.validate_token),
    path('create_client/', views.create_client),
    path('api/update_client/', views.update_client),
    path('api/', include(router.urls)),

    path('api/messages/<str:room_name>/', views.get_messages),
]