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
<<<<<<< HEAD
    path('editarVehiculos/<id>', views.editarVehiculos),
    path('procesarActualizacionVehiculo/', views.procesarActualizacionVehiculo),
=======
    path('login/', views.login),
>>>>>>> 63e3dee588084f0911a8c94ef9845820dad18f1c
    ]