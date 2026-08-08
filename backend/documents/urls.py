from django.urls import path
from .views import home,upload_document,translate_document

urlpatterns=[
    path("",home),
    path("upload/",upload_document), 
    path("translate/",translate_document)                                                                                        

]