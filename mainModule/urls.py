from django.urls import path
from . import views

urlpatterns = [
    path('',views.homepage,name='homepage'),
    path('uploadfile',views.uploadfile,name='uploadfile'),
    path('workpage',views.workpage,name='workpage'),
]
