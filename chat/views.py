from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.viewsets import ModelViewSet
from .models import Person, Room, Message, Note
from rest_framework.authtoken.models import Token
from .serializers import NoteFilter, PersonSerializer, RoomSerializer, MessageSerializer, NoteSerializer
from django.contrib.auth.models import User, Group
from .utils import get_or_create_token, get_user_address, is_admin, is_employee
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from asgiref.sync import async_to_sync


@api_view(['GET'])
def index(request):
    return Response({
        'message': 'Application Running',
        'data': {
            'ip': request.META.get('REMOTE_ADDR'),
            'address': get_user_address(request.META.get('REMOTE_ADDR'))
        },
        'error': 'false'
    }, status=200)



@api_view(['POST'])
def login(request):
    data = request.data
    username = data['username']
    password = data['password']
    try:
        user = User.objects.get(username=username)
    except Exception as e:
        return Response({
            'message': str(e),
            'data': None,
            'error': 'true'
        }, status=201)
    if not is_admin(user) and not is_employee(user):
        return Response({
            'message': 'Unauthorized For Non Employees',
            'data': None,
            'error': 'true'
        }, status=403)
    elif user.check_password(password):
        token = get_or_create_token(user)
        return Response({
            'message': 'Login successful!',
            'data': {'token': token, 'username': user.username, 'group': user.groups.all()[0].name},
            'error': 'false'
        }, status=201)
    else:
        return Response({
            'message': 'Invalid credentials!',
            'data': None,
            'error': 'true'
        }, status=400)


class PersonViewSet(ModelViewSet):
    queryset = Person.objects.all()
    serializer_class = PersonSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['user__groups__name']

    def create(self, request):
        if not is_admin(request.user):
            return Response({
                'message': 'Unauthorized',
                'data': None,
                'error': 'true'
            }, status=401)
        try:
            user = User.objects.create_user(
                username=request.data['username'],
                password=request.data['password'],
                email=request.data['email'],
                first_name = request.data['first_name'],
                last_name = request.data['last_name'],
            )
            group = Group.objects.get(name='employee')
            user.groups.add(group)
            user.save()
            person = Person.objects.create(
                user=user,
                name=user.first_name + ' ' + user.last_name,
                email=user.email,
                address=request.data['address'],
                phone=request.data['phone'],
                ip_address=request.META.get('REMOTE_ADDR')
            )
            person.save()
            serializer = PersonSerializer(person, many=False)
            return Response({
                'message': 'Person created successfully!',
                'data': serializer.data,
                'error': 'false'
            }, status=201)
        except Exception as e:
            return Response({
                'message': str(e),
                'data': None,
                'error': 'true'
            }, status=401)
        
    def update(self, request, *args, **kwargs):
        if not is_admin(request.user) or not kwargs['pk'] == request.user.id:
            return Response({
                'message': 'Unauthorized',
                'data': None,
                'error': 'true'
            }, status=401)
        else:
            id = kwargs['pk']
            user = User.objects.get(id=id)
            user.set_password(request.data['password'])
            user.save()
            return super().update(request, *args, **kwargs)


@api_view(['POST'])
def create_client(request):
    clients = Person.objects.filter(user__groups__name='client').count()
    try:
        user = User.objects.create_user(
        username= "Client#" + str(clients + 1),
        password='qwerty@234',
        email='null',
        first_name='null',
        last_name='null'
        )
        user.groups.add(Group.objects.get(name='client'))
        user.save()
        address = async_to_sync(get_user_address)(request.META.get('REMOTE_ADDR'))
        person = Person.objects.create(
            user=user,
            name=user.first_name + ' ' + user.last_name,
            email=user.email,
            address=address,
            phone='null',
            ip_address=request.META.get('REMOTE_ADDR')
        )
        person.save()
        token = get_or_create_token(user)
        return Response({
            'message': 'Client created successfully!',
            'data': {'token': token, 'username': user.username},
            'error': 'false'
        }, status=201)
    except Exception as e:
        return Response({
            'message': str(e),
            'data': None,
            'error': 'true'
        }, status=401)


@api_view(['POST'])
def validate_token(request):
    token = request.data['token']
    try:
        user = Token.objects.get(key=token).user
        return Response({
            'message': 'Token validated successfully!',
            'data': {'username': user.username},
            'error': 'false'
        })
    except Exception as e:
        return Response({
            'message': str(e),
            'data': None,
            'error': 'true'
        }, status=401)
    


@api_view(['GET'])
def get_messages(request, room_name):
    try:
        room = Room.objects.get(name=room_name)
        messages = Message.objects.filter(room__name=room)
        serializer = MessageSerializer(messages, many=True)
        return Response({
            'message': 'Messages retrieved successfully!',
            'data': serializer.data,
            'error': 'false'
        }, status=200)
    except Exception as e:
        return Response({
            'message': str(e),
            'data': None,
            'error': 'true'
        }, status=404)
    

class NoteViewSet(ModelViewSet):
    queryset = Note.objects.all()
    serializer_class = NoteSerializer
    # permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = NoteFilter

    def create(self, request):
        data = request.data.copy()
        user = Person.objects.get(user=request.user)
        data['user'] = user.id
        data['room'] = Room.objects.get(name=data['room']).id
        try:
            serializer = NoteSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({
                'message': 'Note created successfully!',
                'data': serializer.data,
                'error': 'false'
            })
        except Exception as e:
            return Response({
                'message': str(e),
                'data': None,
                'error': 'true'
            }, status=401)