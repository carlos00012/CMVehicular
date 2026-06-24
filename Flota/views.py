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

        # Buscamos el vehículo seleccionado
        vehiculo_instancia = Vehiculo.objects.get(id=vehiculo_id)

        # Creamos y guardamos el mantenimiento con tus campos exactos del modelo
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
    # 1. Traer todos los mantenimientos para la tabla principal
    mantenimientos = Mantenimiento.objects.all()
    
    # 2. LÓGICA DE REPORTES Y CÁLCULOS
    anio_actual = datetime.now().year
    vehiculos = Vehiculo.objects.all()
    
    PRESUPUESTO_LIMITE = 1000.00  # Límite anual predeterminado por auto (puedes cambiarlo)
    autos_excedidos = []
    
    for auto in vehiculos:
        # Sumamos el costo de todos los talleres de este auto en el año en curso
        gasto_anual = Mantenimiento.objects.filter(
            vehiculo=auto, 
            fecha_servicio__year=anio_actual
        ).aggregate(Sum('costo_taller'))['costo_taller__sum'] or 0
        
        # Le guardamos este cálculo temporalmente al objeto para usarlo en el HTML si fuera necesario
        auto.total_mantenimiento = gasto_anual
        
        # Validamos si superó el tope estipulado
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