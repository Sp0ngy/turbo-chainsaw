from django.urls import path

from . import views

app_name = "ehr"
urlpatterns = [
    path("", views.index, name="index"),
]