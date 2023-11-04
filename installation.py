from chat.models import Person, User
from django.contrib.auth.models import Group

super_user = User.objects.create_superuser(
    username='admin',
    password='qwerty@234',
    email='null',
    first_name='null',
    last_name='null'
)
super_user.save()
person = Person.objects.create(
    user=super_user, profile_picture=None,
    name=super_user.first_name + ' ' + super_user.last_name,
    email=super_user.email, ip_address='127.0.0.1',
    address='Planet Earth', phone='null'
)
person.save()

group_admin = Group.objects.create(name='admin')
group_admin.save()

group_employee = Group.objects.create(name='employee')
group_employee.save()

group_client = Group.objects.create(name='client')
group_client.save()

super_user.groups.add(group_admin)