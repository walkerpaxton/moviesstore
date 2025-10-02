from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.create_petition, name='petition.create'),
    path('<int:id>/vote/', views.vote_petition, name='petition.vote'),
]