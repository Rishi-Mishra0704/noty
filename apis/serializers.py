from rest_framework import serializers
from .models import Note, SharedNote

class NoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = ['id', 'title', 'content', 'created_at', 'updated_at', 'deleted_at', 'owner']
        read_only_fields = ['id', 'created_at', 'updated_at', 'deleted_at', 'owner']

class SharedNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = SharedNote
        fields = ['id', 'note', 'shared_to', 'shared_at']
        read_only_fields = ['id', 'shared_at']

