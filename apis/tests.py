from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from .models import Note, SharedNote

class NoteAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client.force_authenticate(user=self.user)
        self.note = Note.objects.create(title='Test Note', content='Test Content', owner=self.user)
    
    def test_get_note_detail(self):
        url = reverse('note_details', args=[self.note.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Note')
        self.assertEqual(response.data['content'], 'Test Content')
    
    def test_update_note(self):
        url = reverse('note_details', args=[self.note.id])
        updated_content = 'Updated Content'
        response = self.client.put(url, {'content': updated_content}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['detail'], 'Note updated successfully')
        # Check if the note content is updated in the database
        self.note.refresh_from_db()
        self.assertIn(updated_content, self.note.content)
    
    def test_create_note(self):
        url = reverse('note_create')
        data = {'title': 'New Note', 'content': 'New Content'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Note.objects.count(), 2)  # Assuming only one note was created in setUp

    def test_share_note(self):
        other_user = User.objects.create_user(username='otheruser', password='password')
        url = reverse('share_note')
        data = {'note_id': self.note.id, 'shared_to_id': other_user.id}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(SharedNote.objects.filter(note=self.note, shared_to=other_user).exists())
    
    def test_note_history_view(self):
        url = reverse('note_history', args=[self.note.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Ensure correct serialization of history data
        self.assertEqual(len(response.data), 1)  # Assuming there are two versions including the initial one
        # Add more assertions for the content of the history response based on your expectations
    
    def test_note_history_view_no_changes(self):
        # Create a new note without any changes
        new_note = Note.objects.create(title='New Note', content='New Content', owner=self.user)
        url = reverse('note_history', args=[new_note.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Only one version should exist, i.e., the initial creation
    
    def test_note_history_view_non_existent_note(self):
        url = reverse('note_history', args=[999])  # Assuming note with ID 999 does not exist
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)