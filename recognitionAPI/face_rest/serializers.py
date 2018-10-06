from rest_framework import serializers
from face.models import Person
from drf_extra_fields.fields import Base64ImageField

# For base64 image decoder
import re
import base64
import uuid
import imghdr

from django.core.files.base import ContentFile
# -----

def toImage(base64_data):
    # Strip data header if it exists
    # Try to decode the file. Return validation error if it fails.
    try:
        base64_data = re.sub(r"^.+data\:.+base64\,(.+)$", r"\1", base64_data)
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


class PersonSerializer(serializers.ModelSerializer):
    id_mongo = serializers.CharField(required=False)
    image1 = serializers.CharField(required=False, max_length=1000000)
    image2 = serializers.CharField(required=False, max_length=1000000)
    image3 = serializers.CharField(required=False, max_length=1000000) 

    def save(self, **kwargs):
        # Will be done on every save
        print("Id Mongo : ", kwargs['id_mongo'])
        super().save(**kwargs)
        return "User created"

    class Meta:
        model = Person
        fields = ['pk','created','updated','id_mongo','image1','image2','image3']
        
    
