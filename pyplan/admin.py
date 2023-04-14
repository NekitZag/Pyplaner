from django.contrib import admin

# Register your models here.
from .models import Topic, Entry, Session_Groups, Instructors

admin.site.register(Topic)
admin.site.register(Entry)
admin.site.register(Session_Groups)
admin.site.register(Instructors)