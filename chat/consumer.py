import base64
import json
import datetime
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Room, Person, Message, File, Origin
from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
from rest_framework.authtoken.models import Token
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.files.base import ContentFile
import requests

# rooms = []
online_users = []

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"chat_{self.room_name}"
        self.current_room = None

        # ip_addresses = await database_sync_to_async(list)(Origin.objects.filter(access=False, accessor_type="ip"))
        # if self.scope["client"][0] in ip_addresses:
        #     self.close(code=400)

        self.notification_room = "notifications"
        self.notification_room_group = "chat_notifications"

        self.browsing_room = "browsing_room"
        self.browsing_room_group = "chat_browsing_room"

        self.status_room = "status"
        self.status_room_group = "chat_status"

        token = self.scope["query_string"].decode().split("=")[1]
        user_token = await database_sync_to_async(Token.objects.get, thread_sensitive=True)(key=token)

        scheme = self.scope.get("scheme", "http")
        host = self.scope.get("host", "localhost")
        port = self.scope.get("port", "8000")
        uri = self.scope["path"]
        self.current_host = f"{scheme}://{host}:{port}"

        # path, headers, client, server, method

        # ua_string = self.scope["headers"][4][1].decode("utf-8")
        ip_address = self.scope["client"][0]
        self.user_agent_data = await get_user_agent(self.scope["headers"], ip_address)
        # ua_string_list = ua_string.split(" ")

        available_rooms = await sync_to_async(list)(Room.objects.all())
        if self.room_name not in [room.name for room in available_rooms]:
            temp_room = Room.objects.create(name=self.room_name, description='A Room')
            person = await database_sync_to_async(Person.objects.get, thread_sensitive=True)(user=user_token.user)
            temp_room.members.add(person)
            temp_room.save()
            self.current_room = temp_room
        else:
            self.current_room = await database_sync_to_async(Room.objects.get, thread_sensitive=True)(name=self.room_name)

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.channel_layer.group_add(self.browsing_room_group, self.channel_name)
        await self.channel_layer.group_add(self.status_room_group, self.channel_name)
        if not any(user_token.user.username == user["username"] for user in online_users):
            online_users.append({
                "username": user_token.user.username,
                "ip": ip_address,
                "ua": self.user_agent_data,
                "url": self.scope["client"][0]
            })
        await self.channel_layer.group_send(self.status_room_group, {
            "type": "chat_status",
            "users": online_users
        })

        self.user = user_token.user

        await self.channel_layer.group_send(
            self.browsing_room_group, {"type": "chat.browsing", "url": self.current_host, "token": token, "user": self.user.username, "timestamp": str(datetime.datetime.now()).split(".")[0], "msg_type": "none", "room": self.room_name}
        )
        
        if user_token.user.groups.all()[0].name == "admin" or user_token.user.groups.all()[0].name == "employee":
            await self.channel_layer.group_add(self.notification_room_group, self.channel_name)
            
        await self.accept()

    async def disconnect(self, close_code):
        user_to_remove = {
            "username": self.user.username,
            "ip": self.scope["client"][0],
            "ua": self.user_agent_data,
            "url": self.scope["client"][0]
            }
        print(user_to_remove)
        if user_to_remove in online_users:
            online_users.remove(user_to_remove)
        await self.channel_layer.group_send(self.status_room_group, {
            "type": "chat_status",
            "users": online_users
        })
        print(F"{self.user.username}:{self.user_agent_data} disconnected from {self.room_group_name}, status_code: {close_code}")
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        await self.channel_layer.group_discard(self.notification_room_group, self.channel_name)
        await self.channel_layer.group_discard(self.browsing_room_group, self.channel_name)
        await self.close()
        print(F"{self.user.username}:{self.user_agent_data} disconnected from {self.room_group_name}, status_code: {close_code}")


    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        if "message" in text_data_json:
            message = text_data_json["message"]
        
        
        if "url" in text_data_json:
            url = text_data_json["url"]
        user = 'Anonymous'
        timestamp = str(datetime.datetime.now()).split(".")[0]

        if "personal_name" in text_data_json:
            token = text_data_json["token"]
            user_token = await database_sync_to_async(Token.objects.get, thread_sensitive=True)(key=token)
            user_token.user.first_name = text_data_json["personal_name"].split(" ")[0]
            user_token.user.last_name = text_data_json["personal_name"].split(" ")[1]
            user_token.user.save()
            person = await database_sync_to_async(Person.objects.get, thread_sensitive=True)(user=user_token.user)
            person.name = text_data_json["personal_name"]
            person.save()
        if "personal_email" in text_data_json:
            token = text_data_json["token"]
            user_token = await database_sync_to_async(Token.objects.get, thread_sensitive=True)(key=token)
            user_token.user.email = text_data_json["personal_email"]
            user_token.user.save()
            person = await database_sync_to_async(Person.objects.get, thread_sensitive=True)(user=user_token.user)
            person.email = text_data_json["personal_email"]
            person.save()

        room = await database_sync_to_async(Room.objects.get, thread_sensitive=True)(name=self.room_name)

        if "token" in text_data_json:
            token = text_data_json["token"]
            user_token = await database_sync_to_async(Token.objects.get, thread_sensitive=True)(key=token)
            user = user_token.user.username
            person = await database_sync_to_async(Person.objects.get, thread_sensitive=True)(user=user_token.user)


        if "file" in text_data_json:
            uploaded_file_data = text_data_json["file"]
            file_name = uploaded_file_data["name"]
            file_content = uploaded_file_data["content"]
            # file_type = uploaded_file_data["type"]
            file_content = base64.b64decode(file_content)
            # uploaded_file = ContentFile(file_content_bytes, name=file_name)

            if file_name.endswith(".jpg") or file_name.endswith(".jpeg"):
                content_type = "image/jpeg"
            elif file_name.endswith(".png"):
                content_type = "image/png"
            elif file_name.endswith(".pdf"):
                content_type = "application/pdf"
            else:
                content_type = "application/octet-stream"

            uploaded_file = InMemoryUploadedFile(
                ContentFile(file_content),
                field_name=None,
                name=file_name,
                content_type=content_type,
                size=len(file_content),
                charset=None,
            )
            uploaded_file.seek(0)
            file_obj = File.objects.create(
                room=room,
                user=person,
                uploaded_file=uploaded_file
            )
            file_obj.save()
            file_url = f"{self.current_host}{file_obj.uploaded_file.url}"
            message = f"{file_url}"


        if "Welcome to the chat" not in message:
            Message.objects.create(
                sender=person,
                room=room,
                content=message
            ).save()

        await self.channel_layer.group_send(
            self.room_group_name, {"type": "chat.message", "message": message, "token": token, "user": user, "timestamp": timestamp, "room": self.room_name, "msg_type": "msg"}
        )
        await self.channel_layer.group_send(
            self.notification_room_group, {"type": "chat.notification", "message": message, "token": token, "user": user, "timestamp": timestamp, "room": self.notification_room, "msg_type": "msg"}
        )
        await self.channel_layer.group_send(
            self.browsing_room_group, {"type": "chat.browsing", "url": url, "token": token, "user": user, "timestamp": timestamp, "msg_type": "none", "room": self.room_name}
        )

    async def chat_message(self, event):
        message = event["message"]
        token = event["token"]
        timestamp = str(datetime.datetime.now()).split(".")[0]

        user = 'Anonymous'

        user_token = await database_sync_to_async(Token.objects.get, thread_sensitive=True)(key=token)
        user = user_token.user.username

        await self.send(text_data=json.dumps({"message": message, "token": token, "user": user, "timestamp": timestamp, "room": self.room_name, "msg_type": "msg"}))


    async def chat_notification(self, event):
        message = event["message"]
        token = event["token"]
        room_name = event["room"]
        timestamp = str(datetime.datetime.now()).split(".")[0]

        user = 'Anonymous'
        user_token = await database_sync_to_async(Token.objects.get, thread_sensitive=True)(key=token)
        user = user_token.user.username

        await self.send(text_data=json.dumps({"message": message, "token": token, "room": room_name, "timestamp": timestamp, "user": user, "msg_type": "msg"}))


    async def chat_browsing(self, event):
        url = event["url"]
        token = event["token"]

        timestamp = str(datetime.datetime.now()).split(".")[0]

        user = 'Anonymous'
        user_token = await database_sync_to_async(Token.objects.get, thread_sensitive=True)(key=token)
        user = user_token.user.username

        # ip_address = self.scope["client"][0]
        # self.user_agent_data = await get_user_agent(self.scope["headers"], ip_address)

        await self.send(text_data=json.dumps({"url": url, "token": token, "user": user, "timestamp": timestamp, "msg_type": "none", "room": self.room_name}))


    async def chat_status(self, event):
        users = event["users"]
        timestamp = str(datetime.datetime.now()).split(".")[0]

        await self.send(text_data=json.dumps({"timestamp": timestamp, "online_users": users, "msg_type": "none"}))


async def get_user_agent(all_headers, ip_address):
    responseData = {}
    responseData["ip_address"] = ip_address

    for header in all_headers:
        if header[0] == b"user-agent":
            ua_string = header[1].decode("utf-8")

    headers = {
        "Content-Type": "application/json",
    }
    data = {
        "ua": ua_string
    }
    browser = "uknown"
    operating_system = "uknown"
    country_name = "uknown"

    try:
        # country = requests.get(f"https://api.country.is/{ip_address}").json()
        country_name = requests.get(f"https://ipapi.co/json/", timeout=10).json()["country_name"]
        responseData["country"] = country_name
    except:
        responseData["country"] = country_name

    try:
        res = requests.post("https://api.apicagent.com", headers=headers, json=data, timeout=10)
        res = res.json()
        browser = res["client"]
        operating_system = res["os"]
        responseData["browser"] = browser["name"] + " " + browser['version'].split('.')[0]
        responseData["operating_system"] = operating_system['name'] + " " + operating_system['version'] + " " + operating_system['platform']
    except Exception as e:
        responseData["browser"] = browser
        responseData["operating_system"] = operating_system
        responseData["country"] = country_name
        responseData["ip_address"] = ip_address
    
    return responseData