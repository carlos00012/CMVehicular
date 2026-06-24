from django.shortcuts import render, redirect
from .models import Vehiculo, Mantenimiento
from django.contrib import messages
# Create your views here.

def inicio(request):
    return render(request, "inicio.html")

def nuevoVehiculo(request):
    return render(request, "nuevoVehiculo.html")

def guardarVehiculo(request):
    if request.method == 'POST':
        foto = request.FILES.get('foto')
        placa = request.POST.get('placa')
        tipo_vehiculo = request.POST.get('tipo_vehiculo')
        tipo_combustible = request.POST.get('tipo_combustible')
        seguro_vigente = request.POST.get('seguro_vigente') == 'on'
        anio_modelo = request.POST.get('anio_modelo')

        vehiculo = Vehiculo(
            foto=foto,
            placa=placa,
            tipo_vehiculo=tipo_vehiculo,
            tipo_combustible=tipo_combustible,
            seguro_vigente=seguro_vigente,
            anio_modelo=anio_modelo
        )
        vehiculo.save()
        messages.success(request, 'Vehículo guardado correctamente.')
        return redirect('/listadoVehiculos/')  # Redirige a la página de inicio después de guardar el vehículo

def listadoVehiculos(request):
    vehiculos = Vehiculo.objects.all()
    return render(request, "listadoVehiculos.html", {"misvehiculos": vehiculos})


def eliminarVehiculo(request, id):
    vehiculoEliminar = Vehiculo.objects.get(id=id)
    vehiculoEliminar.delete()
    messages.success(request, 'Vehículo eliminado correctamente.')
    return redirect('/listadoVehiculos/')