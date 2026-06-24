from django.urls import path
from . import views

urlpatterns = [
    path('', views.inicio),
    path('nuevoVehiculo/', views.nuevoVehiculo),
    path('guardarVehiculo/', views.guardarVehiculo),
    path('listadoVehiculos/', views.listadoVehiculos),
    path('eliminarVehiculo/<id>', views.eliminarVehiculo),
    path('nuevoMantenimiento/', views.nuevoMantenimiento),
    path('guardarMantenimiento/', views.guardarMantenimiento),
    path('listadoMantenimientos/', views.listadoMantenimientos),
    path('editarVehiculos/<id>', views.editarVehiculos),
    path('procesarActualizacionVehiculo/', views.procesarActualizacionVehiculo),
    ]