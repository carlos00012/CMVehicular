from django.shortcuts import render, redirect
from .models import Vehiculo, Mantenimiento
from django.contrib import messages
#Sirve para hacer sumatorias de campos en la base de datos
from django.db.models import Sum
#Sirve para obtener la fecha actual y manipularla
from datetime import datetime
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



def nuevoMantenimiento(request):
    # Traemos los vehículos para llenar la lista desplegable del formulario
    vehiculos = Vehiculo.objects.all()
    return render(request, "nuevoMantenimiento.html", {"vehiculos": vehiculos})


def guardarMantenimiento(request):
    if request.method == 'POST':
        vehiculo_id = request.POST.get('vehiculo')
        pdf = request.FILES.get('pdf')
        fecha_servicio = request.POST.get('fecha_servicio')
        costo_taller = request.POST.get('costo_taller')
        tipo_mantenimiento = request.POST.get('tipo_mantenimiento')
        repuestos_cambiados = request.POST.get('repuestos_cambiados')
        vehiculo_instancia = Vehiculo.objects.get(id=vehiculo_id)
        mantenimiento = Mantenimiento(
            vehiculo=vehiculo_instancia,
            pdf=pdf,
            fecha_servicio=fecha_servicio,
            costo_taller=costo_taller,
            tipo_mantenimiento=tipo_mantenimiento,
            repuestos_cambiados=repuestos_cambiados
        )
        mantenimiento.save()
        messages.success(request, 'Mantenimiento guardado correctamente.')
        return redirect('/listadoMantenimientos/')


def listadoMantenimientos(request):
    mantenimientos = Mantenimiento.objects.all()
    anio_actual = datetime.now().year
    vehiculos = Vehiculo.objects.all()
    PRESUPUESTO_LIMITE = 1000.00  # Límite anual predeterminado por auto 
    autos_excedidos = []
    for auto in vehiculos:
        # Sumamos el costo de todos los talleres de este auto en el año en curso
        gasto_anual = Mantenimiento.objects.filter(
            vehiculo=auto, 
            fecha_servicio__year=anio_actual
        ).aggregate(Sum('costo_taller'))['costo_taller__sum'] or 0
        # Le guardamos este cálculo temporalmente al objeto para usarlo en el HTML si fuera necesario
        auto.total_mantenimiento = gasto_anual
        # Validamos si superó el tope 
        if gasto_anual > PRESUPUESTO_LIMITE:
            autos_excedidos.append({
                'placa': auto.placa,
                'tipo': auto.tipo_vehiculo,
                'gastado': gasto_anual,
                'limite': PRESUPUESTO_LIMITE,
                'exceso': gasto_anual - PRESUPUESTO_LIMITE
            })
    return render(request, "listadoMantenimientos.html", {
        "mismantenimientos": mantenimientos,
        "autos_excedidos": autos_excedidos
    })


def editarVehiculos(request, id):
    vehiculoEditar = Vehiculo.objects.get(id=id)
    return render(request, 'editarVehiculos.html', {'vehiculo': vehiculoEditar})

#Procesando actualizacion de vehiculos
def procesarActualizacionVehiculo(request):
    if request.method == 'POST':
        id = request.POST.get('id')
        placa = request.POST.get('placa')
        tipo_vehiculo = request.POST.get('tipo_vehiculo')
        tipo_combustible = request.POST.get('tipo_combustible')
        
        # Al usar .get() con la comparación '== on', si no viene en el POST se evalúa automáticamente como False
        seguro_vigente = request.POST.get('seguro_vigente') == 'on'
        anio_modelo = request.POST.get('anio_modelo')
        
        vehiculoEditar = Vehiculo.objects.get(id=id)
        
        vehiculoEditar.placa = placa
        vehiculoEditar.tipo_vehiculo = tipo_vehiculo
        vehiculoEditar.tipo_combustible = tipo_combustible
        vehiculoEditar.seguro_vigente = seguro_vigente
        vehiculoEditar.anio_modelo = anio_modelo
        
        # Procesar la foto si se subió una nueva
        nueva_foto = request.FILES.get('foto')
        if nueva_foto:
            if vehiculoEditar.foto:
                import os
                if os.path.isfile(vehiculoEditar.foto.path):
                    os.remove(vehiculoEditar.foto.path)
            vehiculoEditar.foto = nueva_foto
        
        vehiculoEditar.save()
        messages.success(request, 'Vehículo actualizado correctamente.')
        return redirect('/listadoVehiculos/')


def login(request):
    return render(request, "login.html")

