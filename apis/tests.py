from django.urls import reverse
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from .models import Note

class NoteAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.force_authenticate(user=self.user)
        self.note = Note.objects.create(title='Test Note', content='Test Content', owner=self.user)

    def test_note_detail(self):
        url = reverse('note_details', kwargs={'note_id': self.note.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_note_update(self):
        url = reverse('note_details', kwargs={'note_id': self.note.id})
        data = {'content': 'Updated Content'}
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertIn('Note updated successfully', response.data['detail'])

    def test_note_create(self):
        url = reverse('note_create')
        data = {'title': 'New Note', 'content': 'New Content'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 201)

    def test_share_note(self):
        # Create another user
        shared_to_user = User.objects.create_user(username='shareduser', password='sharedpassword')
        url = reverse('share_note')
        data = {'note_id': self.note.id, 'shared_to_id': shared_to_user.id}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 201)
