from django.urls import path
from .views import note_detail,note_create
urlpatterns = [
    path('note/<int:note_id>', note_detail, name="note_details"),
    path('note/', note_create, name="note_create"),
]
