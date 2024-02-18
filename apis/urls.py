from django.urls import path
from .views import note,note_create,share_note,note_history_view
urlpatterns = [
    path('notes/<int:note_id>', note, name="note_details"),
    path('notes/create/', note_create, name="note_create"),
    path('notes/share/', share_note, name="share_note"),
    path('notes/version-history/<int:note_id>', note_history_view, name="share_note"),


]
