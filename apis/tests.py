from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from .models import Note, SharedNote
from .serializers import NoteSerializer, SharedNoteSerializer
from rest_framework import status

class APITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

    def test_note_create(self):
        url = reverse('note_create')
        data = {'title': 'Test Note', 'content': 'This is a test note.'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Note.objects.filter(title='Test Note').exists())
        created_note = Note.objects.get(title='Test Note')
        self.assertEqual(NoteSerializer(created_note).data, response.data)

    def test_note_get(self):
        note = Note.objects.create(title='Test Note', content='This is a test note.', owner=self.user)
        url = reverse('note_details', args=[note.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, NoteSerializer(note).data)

    def test_note_update(self):
        note = Note.objects.create(title='Test Note', content='This is a test note.', owner=self.user)
        url = reverse('note_details', args=[note.id])
        data = {'title': 'Updated Note', 'content': 'This is an updated note.'}
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        updated_note = Note.objects.get(id=note.id)
        self.assertEqual(updated_note.title, 'Updated Note')
        self.assertEqual(NoteSerializer(updated_note).data, response.data)

    def test_share_note(self):
        shared_to_user = User.objects.create_user(username='shareduser', password='testpassword')
        note = Note.objects.create(title='Test Note', content='This is a test note.', owner=self.user)
        url = reverse('share_note')
        data = {'note_id': note.id, 'shared_to_id': shared_to_user.id}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(SharedNote.objects.filter(note=note, shared_to=shared_to_user).exists())
        created_shared_note = SharedNote.objects.get(note=note, shared_to=shared_to_user)
        self.assertEqual(SharedNoteSerializer(created_shared_note).data, response.data)
