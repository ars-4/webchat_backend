from rest_framework import serializers
from .models import Room, Message, Person, Note
import django_filters


class PersonSerializer(serializers.ModelSerializer):
    user_name = serializers.ReadOnlyField(source='user.username')
    user_id = serializers.ReadOnlyField(source='user.id')
    group_name = serializers.ReadOnlyField(source='user.groups.first.name')
    class Meta:
        model = Person
        fields = ['user_name', 'user_id', 'group_name', 'profile_picture', 'name', 'email', 'address', 'phone', 'date_created', 'date_updated', 'ip_address']

class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ['name', 'description', 'members', 'date_created', 'date_updated']

class MessageSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='sender.user.username')
    message = serializers.ReadOnlyField(source='content')
    timestamp = serializers.ReadOnlyField(source='date_created')
    class Meta:
        model = Message
        fields = ['room', 'user', 'message', 'timestamp']

class NoteSerializer(serializers.ModelSerializer):
    user_name = serializers.ReadOnlyField(source='user.user.username')
    room_name = serializers.StringRelatedField(source='room.name', read_only=True)
    class Meta:
        model = Note
        fields = ['id', 'room', 'user', 'user_name', 'content', 'room_name', 'date_created', 'date_updated']


class NoteFilter(django_filters.FilterSet):
    room__name = django_filters.CharFilter(field_name='room__name', lookup_expr='icontains')
    class Meta:
        model = Note
        fields = ['id', 'room', 'user', 'content', 'room__name', 'date_created', 'date_updated']