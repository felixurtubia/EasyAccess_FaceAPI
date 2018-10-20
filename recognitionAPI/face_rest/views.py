from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.exceptions import NotAuthenticated
#rom face_rest.serializers import PersonImageSerializer
from face_rest.serializers import PersonSerializer
from face.models import Person, Guest, Building
from django.contrib.auth.models import User
from recognitionAPI.startup import predict
import face_recognition
from sklearn import neighbors
import pickle
import math
from datetime import datetime

from rest_framework.views import APIView
from rest_framework import authentication, permissions
from rest_framework.response import Response
from recognitionAPI.startup import run
import os
from django.conf import settings

# For base64 image decoder
import re
import base64
import uuid
import imghdr

from django.core.files.base import ContentFile
# -----

def toImage(base64_data):
    # Strip data header if it exists
    print("Aqui va la imagen")
    print(base64_data)
    base64_data = re.sub(r"^data\:.+base64\,(.+)$", r"\1", base64_data)

    # Try to decode the file. Return validation error if it fails.
    try:
        decoded_file = base64.b64decode(base64_data)
    except TypeError:
        msg = "Please upload a valid image."
        print(msg)

    # Get the file name extension:
    extension = imghdr.what("file_name", decoded_file)
    if extension not in ("jpeg", "jpg", "png"):
        msg = "{0} is not a valid image type.".format(extension)
        print(msg)


    extension = "jpg" if extension == "jpeg" else extension
    file_name = ".".join([str(uuid.uuid4()), extension])
    data = ContentFile(decoded_file, name=file_name)
    return data


def prediction(image, model_path=None, distance_threshold=0.5):
    """
    Recognizes an image from request 
    """
    newFace = face_recognition.load_image_file(image)
    newFaceLocations = face_recognition.face_locations(newFace)

    if len(newFaceLocations) == 0:
        return [2, "No Faces Found"]
    """
    There is something then
    """
    new_faces_encodings = face_recognition.face_encodings(newFace, known_face_locations=newFaceLocations)

    personas = Person.objects.all()
    for persona in personas:
        encoding1 = persona.image1.split(',')
        encoding1 = [float(item) for item in encoding1]
        match1 = face_recognition.compare_faces([encoding1], new_faces_encodings[0])
        if match1[0]:
            return [0, persona.id_mongo, persona]

        encoding2 = persona.image2.split(',')
        encoding2 = [float(item) for item in encoding2]
        match2 = face_recognition.compare_faces([encoding2], new_faces_encodings[0])
        if match2[0]:
            return [0, persona.id_mongo, persona]
            
        encoding3 = persona.image3.split(',')
        encoding3 = [float(item) for item in encoding3]
        match3 = face_recognition.compare_faces([encoding3], new_faces_encodings[0])
        if match3[0]:
            return [0, persona.id_mongo, persona]

    return [1, "Something Happened"]


class PersonViewSet(viewsets.ModelViewSet):
    queryset = Person.objects.all()
    serializer_class = PersonSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response("User created", status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        #Se reciben las imagenes en base64, se traspasan a archivo y se sacan los encodings para serializar
        image1 = toImage(self.request.data.get('image1'))
        image1 = face_recognition.face_encodings(face_recognition.load_image_file(image1))[0]
        image1 = ','.join(str(item) for item in image1)
        date_1 = datetime.now()
        image2 = toImage(self.request.data.get('image2'))
        image2 = face_recognition.face_encodings(face_recognition.load_image_file(image2))[0]
        image2 = ','.join(str(item) for item in image2)
        date_2 = datetime.now()
        image3 = toImage(self.request.data.get('image3'))
        image3 = face_recognition.face_encodings(face_recognition.load_image_file(image3))[0]
        image3 = ','.join(str(item) for item in image3)
        date_3 = datetime.now()

        serializer.save(id_mongo=self.request.data.get('idMongo'),
                            image1=image1,
                            date_image1=date_1,
                            image2=image2,
                            date_image2=date_2,
                            image3=image3,
                            date_image3=date_3)


class guests(APIView):
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.AllowAny,)

    def get(self, request, format=None):
        """
        List all Guests ID's and Creators ID's
        """
        guests = Guest.objects.all()
        ids = [[guest.id_mongo, guest.id_creador] for guest in Guest]
        return ids
    
    def post(self, request, format=None):
        """
        Ceación de un invitado
        """
        try:
            id_mongo = request.data.get('idMongo')
            id_creador = request.data.get('idCreador')
        except:
            return Response(status=status.HTTP_204_NO_CONTENT)

        data = request.data
        image1 = toImage(data.get('image1'))
        image1 = face_recognition.face_encodings(face_recognition.load_image_file(image1))[0]
        image1 = ','.join(str(item) for item in image1)
        image2 = toImage(data.get('image2'))
        image2 = face_recognition.face_encodings(face_recognition.load_image_file(image2))[0]
        image2 = ','.join(str(item) for item in image2)
        image3 = toImage(data.get('image3'))
        image3 = face_recognition.face_encodings(face_recognition.load_image_file(image3))[0]
        image3 = ','.join(str(item) for item in image3)

        guest = Guest()
        guest.image1 = image1
        guest.image2 = image2
        guest.image3 = image3
        guest.date_image1 = datetime.now()
        guest.date_image2 = datetime.now()
        guest.date_image3 = datetime.now()
        guest.id_mongo = id_mongo
        guest.id_creador = id_creador
        return Response(status=status.HTTP_201_CREATED)


class getId(APIView):
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.AllowAny,)

    def get(self, request, format=None):
        """
        Listar todos los id de los residentes
        """
        ids = [person.id_mongo for person in Person.objects.all()]
        return Response(ids)

    def post(self, request, format=None):
        """
        Post para identificar una persona
        """
        image = toImage(self.request.data.get('image'))
        matching = prediction(image)
        matching_status = matching[0]

        if matching_status == 0:
            """User Identified Correctly"""
            updateUserImage(image, matching[2])
            return Response(status=status.HTTP_202_ACCEPTED ,data = matching[1])
        elif matching_status == 1:
            """User Not Identified"""
            return Response(status=status.HTTP_403_FORBIDDEN)
        elif matching_status == 2:
            """Invalid Foto"""
            return Response()
        elif matching_status == 3:
            """More Than one USer in the Foto"""
            return Response()
        else:
            """There was an unknown problem"""
            return Response()


def updateUserImage(image, user):
    print("Updating user image")
    image = face_recognition.face_encodings(face_recognition.load_image_file(image))[0]
    image = ','.join(str(item) for item in image)
    """user = Person.objects.get(id_mongo=id_mongo)
    user = user[0]"""
    print("El usuario es:  ", user)

    date_1 = user.date_image1
    date_2 = user.date_image2
    date_3 = user.date_image3


    if(date_1 > date_2 and date_1 > date_3):
        user.date_1 = datetime.now()
        user.image1 = image
        user.save()
    if(date_2 > date_1 and date_2 > date_3):
        user.date_2 = datetime.now()
        user.image2 = image
        user.save()
    if(date_3 > date_2 and date_3 > date_1):
        user.date_3 = datetime.now()
        user.image3 = image
        user.save()
    else:
        print("Ocurrió un problema con las fechas")
