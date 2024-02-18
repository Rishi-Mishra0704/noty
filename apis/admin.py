from django.contrib import admin
from .models import Note, SharedNote,NoteVersion
# Register your models here.


admin.site.register(Note)
admin.site.register(SharedNote)
admin.site.register(NoteVersion)