from django.urls import path

from . import views

urlpatterns = [
    path("saude/", views.saude, name="saude"),
    path("", views.menu, name="menu"),
    path("retirada/", views.retirada, name="retirada"),
    path("retirada/<int:familia_id>/registrar/", views.registrar, name="registrar"),
    path("estoque/", views.estoque, name="estoque"),
]
