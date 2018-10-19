from django.conf.urls import url, include
from rest_framework import routers
from face_rest.views import PersonViewSet
from face_rest.views import getId
from face_rest.views import guests 


router = routers.DefaultRouter()
router.register('Persons', PersonViewSet, 'Persons' )
#router.register('PersonImages', PersonImageViewSet, 'PersonImages')

urlpatterns = [
    url(r'getId',getId.as_view()),
    url(r'guests', guests.as_view()),
    url(r'^', include(router.urls)),
]