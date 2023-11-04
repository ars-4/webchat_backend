from django.contrib.auth.models import User, Group
from chat.models import Person

super_user = User.objects.create_superuser('admin', 'admin@thissite.org', 'Qwerty@234')
super_user.save()
person = Person.objects.create(
    user=super_user, profile_picture=None,
    name='Administrator',
    email='admin@thissite.org', ip_address='127.0.0.1',
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