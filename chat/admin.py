from django.contrib import admin
from .models import Person, Room, Message, Note, File, Origin

admin.site.register(Person)
admin.site.register(Room)
admin.site.register(Message)
admin.site.register(Note)
admin.site.register(File)
admin.site.register(Origin)

