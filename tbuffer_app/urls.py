from django.urls import path
from . import views

urlpatterns = [
  path('',        views.index,        name='home'),
  path('encrypt/',views.encrypt_view, name='encrypt'),
  path('decrypt/',views.decrypt_view, name='decrypt'),
]
