from django.urls import path
from . import views

urlpatterns = [
    path('show-username/', views.show_username, name='show-username'),
]
