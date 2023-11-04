from django.db import models
from django.contrib.auth.models import User


class BaseModel(models.Model):
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    class Meta:
        abstract = True


class Person(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='profile_pictures', blank=True)
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=100, blank=True)
    ip_address = models.CharField(max_length=100, blank=True, null=True)
    address = models.CharField(max_length=200, default="Planet Earth")
    phone = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.user.username

class Room(BaseModel):
    name = models.CharField(max_length=100)
    description = models.TextField()
    members = models.ManyToManyField(Person)

    def __str__(self):
        return self.name

class Message(BaseModel):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    sender = models.ForeignKey(Person, on_delete=models.CASCADE)
    content = models.TextField()

    def __str__(self):
        return self.sender.user.username
    
class Note(BaseModel):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    user = models.ForeignKey(Person, on_delete=models.CASCADE)
    content = models.TextField()

    def __str__(self):
        return self.user.user.username
    

class File(BaseModel):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    user = models.ForeignKey(Person, on_delete=models.CASCADE)
    uploaded_file = models.FileField(upload_to='files')

    def __str__(self):
        return self.user.user.username


class Origin(BaseModel):
    accessor = models.CharField(max_length=200)
    access = models.BooleanField(default=False)
    accessor_type = models.CharField(max_length=100, choices=(
        ('ip', 'ip'),
        ('website', 'website')
    ))

    def __str__(self):
        return self.accessor
    

