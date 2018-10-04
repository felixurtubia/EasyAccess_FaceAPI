from django.db import models
from face_recognition import load_image_file, face_encodings

# Create your models here.


class Person(models.Model):
    """
    Clase para guardar datos de cada persona agregada al modelo, se guarda la fecha de creación,
    la fecha de actualización y el id que tiene la persona en mongodb (eso es lo que se entrega)
    """
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    id_mongo = models.CharField(null=True, max_length=10000)
    image1 = models.CharField(null=True, max_length=100000000)
    image2 = models.CharField(null=True, max_length=100000000)
    image3 = models.CharField(null=True, max_length=100000000)

    class Meta:
        ordering = ('created',)
