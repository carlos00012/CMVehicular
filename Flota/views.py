from django.shortcuts import render, redirect
from .models import Vehiculo, Mantenimiento
# Create your views here.

def inicio(request):
    return render(request, "inicio.html")
