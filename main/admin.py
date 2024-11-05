from django.contrib import admin

from .models import Message, Pet, Preferences

admin.site.register(Pet)
admin.site.register(Preferences)
admin.site.register(Message)
