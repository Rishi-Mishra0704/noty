from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.utils import timezone

from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Note, SharedNote
from .serializers import NoteHistorySerializer, SharedNoteSerializer, NoteSerializer

@api_view(['GET', 'PUT'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def note(request, note_id):
    """
    Retrieve or update a note.

    GET: Retrieve the note details.
    PUT: Update the note content.

    Args:
        request: HTTP request object.
        note_id: ID of the note to retrieve or update.

    Returns:
        HTTP response with the note details or update status.
    """
    try:
        note = Note.objects.get(pk=note_id)
    except Note.DoesNotExist:
        return Response({'detail': 'Note not found'}, status=status.HTTP_404_NOT_FOUND)

    if not request.user.is_superuser and request.user != note.owner and not SharedNote.objects.filter(note=note, shared_to=request.user).exists():
        return Response({'detail': 'You do not have permission to edit this note'}, status=status.HTTP_403_FORBIDDEN)

    if request.method == 'GET':
        if request.user == note.owner or request.user in note.shared_users.all():
            serializer = NoteSerializer(note)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'detail': 'You do not have permission to view this note'}, status=status.HTTP_403_FORBIDDEN)

    elif request.method == 'PUT':
        updated_content = request.data.get('content')
        if updated_content is None:
            return Response({'detail': 'Content is required for updating the note'}, status=status.HTTP_400_BAD_REQUEST)

        note.content += '\n' + updated_content
        note.updated_at = timezone.now()
        note.save()

        return Response({'detail': 'Note updated successfully'}, status=status.HTTP_200_OK)

    # Handle invalid HTTP method
    return Response({'detail': 'Method not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def note_create(request):
    """
    Create a new note.

    Args:
        request: HTTP request object.

    Returns:
        HTTP response with the created note details or validation errors.
    """
    serializer = NoteSerializer(data=request.data)
    if serializer.is_valid():
        serializer.validated_data['owner'] = request.user
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def share_note(request):
    """
    Share a note with another user.

    Args:
        request: HTTP request object.

    Returns:
        HTTP response with the shared note details or error message.
    """
    try:
        note_id = request.data.get('note_id')
        shared_to_id = request.data.get('shared_to_id')
        note = Note.objects.get(pk=note_id)
        shared_to_user = User.objects.get(pk=shared_to_id)
    except (Note.DoesNotExist, User.DoesNotExist):
        return Response({'detail': 'Note or user not found'}, status=status.HTTP_404_NOT_FOUND)

    if note.owner != request.user:
        return Response({'detail': 'You do not have permission to share this note'}, status=status.HTTP_403_FORBIDDEN)

    shared_note = SharedNote.objects.create(
        note=note, shared_to=shared_to_user)
    serializer = SharedNoteSerializer(shared_note)
    return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def note_history(request, note_id):
    """
    Retrieve the version history of a note.

    Args:
        request: HTTP request object.
        note_id: ID of the note to retrieve history for.

    Returns:
        HTTP response with the version history of the note.
    """
    note = get_object_or_404(Note, id=note_id)
    history = note.history.all()
    
    since_creation_history = [version for version in history if version.history_date >= note.created_at]
    
    serializer = NoteHistorySerializer(since_creation_history, many=True)
    return Response(serializer.data)
