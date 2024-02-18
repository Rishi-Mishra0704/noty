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
    
    def test_get_existing_note(self):
        url = reverse('note', args=[self.note.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Note')
        self.assertEqual(response.data['content'], 'Test Content')
    
    def test_get_non_existing_note(self):
        url = reverse('note', args=[999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['detail'], 'Note not found')
    
    def test_get_note_without_permission(self):
        other_user = User.objects.create_user(username='otheruser', password='password')
        self.client.force_authenticate(user=other_user)
        url = reverse('note', args=[self.note.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_update_note_with_valid_content(self):
        url = reverse('note', args=[self.note.id])
        updated_content = 'Updated Content'
        response = self.client.put(url, {'content': updated_content}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['detail'], 'Note updated successfully')
        self.note.refresh_from_db()
        self.assertIn(updated_content, self.note.content)
    
    def test_update_note_with_missing_content(self):
        url = reverse('note', args=[self.note.id])
        response = self.client.put(url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['detail'], 'Content is required for updating the note')
        # Ensure note content is not changed
        self.note.refresh_from_db()
        self.assertNotEqual(self.note.content, '')
    
    def test_update_note_without_permission(self):
        other_user = User.objects.create_user(username='otheruser', password='password')
        self.client.force_authenticate(user=other_user)
        url = reverse('note', args=[self.note.id])
        response = self.client.put(url, {'content': 'Updated Content'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['detail'], 'You do not have permission to edit this note')
    
    def test_invalid_http_method(self):
        url = reverse('note', args=[self.note.id])
        response = self.client.post(url, {}, format='json') 
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(response.data['detail'], 'Method "POST" not allowed.')
    
    def test_create_note(self):
        url = reverse('note_create')
        data = {'title': 'New Note', 'content': 'New Content'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Note.objects.count(), 2)

    def test_share_note(self):
        other_user = User.objects.create_user(username='otheruser', password='password')
        url = reverse('share_note')
        data = {'note_id': self.note.id, 'shared_to_id': other_user.id}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(SharedNote.objects.filter(note=self.note, shared_to=other_user).exists())
    
    def test_share_note_invalid_user(self):
        url = reverse('share_note')
        data = {'note_id': self.note.id, 'shared_to_id': 999}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['detail'], 'Note or user not found')
    
    def test_share_note_invalid_note(self):
        url = reverse('share_note')
        data = {'note_id': 999, 'shared_to_id': self.user.id}  
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['detail'], 'Note or user not found')
    
    def test_share_note_permission_denied(self):
        other_user = User.objects.create_user(username='otheruser', password='password')
        url = reverse('share_note')
        data = {'note_id': self.note.id, 'shared_to_id': other_user.id}
        self.client.force_authenticate(user=other_user)
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['detail'], 'You do not have permission to share this note')
    
    def test_note_history_view(self):
        url = reverse('note_history', args=[self.note.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  
    
    def test_note_history_view_no_changes(self):
        new_note = Note.objects.create(title='New Note', content='New Content', owner=self.user)
        url = reverse('note_history', args=[new_note.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_note_history_view_non_existent_note(self):
        url = reverse('note_history', args=[999]) 
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)