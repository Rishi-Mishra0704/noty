from django.db import models
from django.contrib.auth.models import User

class Note(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

class SharedNote(models.Model):
    note = models.ForeignKey(Note, related_name='shared_notes', on_delete=models.CASCADE)
    shared_to = models.ForeignKey(User, related_name='shared_notes_received', on_delete=models.CASCADE)
    shared_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.note.owner.username} passed note to {self.shared_to.username}"


class NoteVersion(models.Model):
    note = models.ForeignKey(Note, related_name='versions', on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    changes = models.TextField()

    def __str__(self):
        return f"Version {self.id} of Note {self.note.id}"