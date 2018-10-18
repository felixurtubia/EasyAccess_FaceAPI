from django.db import models
from face_recognition import load_image_file, face_encodings

# Create your models here.

class Building(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    name = models.CharField(null=True, max_length=1000)
    
class Person(models.Model):
    """
    Clase para guardar datos de cada persona agregada al modelo, se guarda la fecha de creación,
    la fecha de actualización y el id que tiene la persona en mongodb (eso es lo que se entrega)
    """
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    id_mongo = models.CharField(null=True, max_length=10000)
    id_creador = models.CharField(null=True, max_length=10000)
    image1 = models.CharField(null=True, max_length=100000000)
    date_image1 = models.DateTimeField(null=True,auto_now=False)
    image2 = models.CharField(null=True, max_length=100000000)
    date_image2 = models.DateTimeField(null=True)
    image3 = models.CharField(null=True, max_length=100000000)
    date_image3 = models.DateTimeField(null=True)

    class Meta:
        ordering = ('created',)

class Guest(models.Model):
    """
    Clase para invitados creados por usuarios
    """
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    id_mongo = models.CharField(null=True, max_length=10000)
    id_creador = models.CharField(null=True, max_length=10000)
    image1 = models.CharField(null=True, max_length=100000000)
    date_image1 = models.DateTimeField(null=True,auto_now=False)
    image2 = models.CharField(null=True, max_length=100000000)
    date_image2 = models.DateTimeField(null=True)
    image3 = models.CharField(null=True, max_length=100000000)
    date_image3 = models.DateTimeField(null=True)
    creador = models.ForeignKey(Person, on_delete=models.CASCADE, null=True)

