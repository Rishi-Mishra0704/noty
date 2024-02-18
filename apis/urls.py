from django.urls import path
from .views import note,note_create
urlpatterns = [
    path('notes/<int:note_id>', note, name="note_details"),
    path('notes/create/', note_create, name="note_create"),
]
