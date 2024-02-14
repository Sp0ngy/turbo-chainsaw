from django.urls import path

from . import views

app_name = "ehr"
urlpatterns = [
    path("pseudonymize", views.pseudonymize_data, name="pseudonymize_data"),
    path("de-pseudonymize", views.de_pseudonymize_data, name="de-pseudonymize_data")
]