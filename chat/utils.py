from rest_framework.authtoken.models import Token
from django.contrib.auth.models import Group
import requests

def get_or_create_token(user):
    try:
        token = Token.objects.get(user=user)
    except Token.DoesNotExist:
        token = Token.objects.create(user=user)
    return token.key


def is_admin(user):
    if user.groups.all()[0].name == 'admin':
        return True
    return False

def is_employee(user):
    if user.groups.all()[0].name == 'employee':
        return True
    return False


async def get_user_address(ip_address):
    try:
        res = await requests.get(f"https://ipapi.co/{ip_address}/json/").json()
        return res["city"] + ", " + res["country_name"]
    except Exception as e:
        return "Self"