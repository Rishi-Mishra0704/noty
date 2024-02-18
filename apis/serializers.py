from rest_framework import serializers
from .models import Note, SharedNote

class NoteHistorySerializer(serializers.ModelSerializer):
    user_made_change = serializers.SerializerMethodField()

    def get_user_made_change(self, obj):
        return obj.history_user.username if obj.history_user else "Unknown"

    class Meta:
        model = Note
        fields = ['id', 'title', 'content', 'created_at', 'updated_at', 'deleted_at', 'owner', 'user_made_change']

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

