from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework import status


from .models import Note
from .serializers import SharedNoteSerializer, NoteSerializer
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

# Create your views here.


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def note_detail(request, note_id):

    try:
        note = Note.objects.get(pk=note_id)
    except note.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    serializer = NoteSerializer(note)
    return Response(serializer.data, status=status.HTTP_200_OK)



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