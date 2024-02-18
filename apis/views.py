from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework import status
from django.contrib.auth.models import User


from .models import Note
from .serializers import SharedNoteSerializer, NoteSerializer
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

# Create your views here.


@api_view(['GET', 'PUT'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def note(request, note_id):
    try:
        note = Note.objects.get(pk=note_id)
    except Note.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = NoteSerializer(note)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'PUT':
        serializer = NoteSerializer(note, data=request.data)
        if serializer.is_valid():
            serializer.validated_data['owner'] = request.user
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def note_create(request):
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
    try:
        note_id = request.data.get('note_id')
        shared_to_id = request.data.get('shared_to_id')
        note = Note.objects.get(pk=note_id)
        shared_to_user = User.objects.get(pk=shared_to_id)
    except (Note.DoesNotExist, User.DoesNotExist):
        return Response({'detail': 'Note or user not found'}, status=status.HTTP_404_NOT_FOUND)

    if note.owner != request.user:
        return Response({'detail': 'You do not have permission to share this note'}, status=status.HTTP_403_FORBIDDEN)

    shared_note_data = {
        'note': note,
        'shared_from': request.user,
        'shared_to': shared_to_user
    }
    serializer = SharedNoteSerializer(data=shared_note_data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)