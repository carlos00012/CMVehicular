from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Sum
from datetime import datetime
from decimal import Decimal
from .models import Vehiculo, Mantenimiento, PerfilUsuario, ReporteFalla

# ============ FUNCIONES DE VERIFICACIÓN ============
def es_gerente(user):
    try:
        return user.is_authenticated and user.perfil.tipo_perfil == 'gerente'
    except:
        return False

def es_chofer(user):
    try:
        return user.is_authenticated and user.perfil.tipo_perfil == 'chofer'
    except:
        return False

# ============ VISTA DE INICIO ============
def inicio(request):
    if request.user.is_authenticated:
        try:
            perfil = request.user.perfil
            if perfil.tipo_perfil == 'gerente':
                return redirect('dashboard_gerente')
            elif perfil.tipo_perfil == 'chofer':
                return redirect('dashboard_chofer')
        except:
            pass
    return render(request, "login.html")

# ============ LOGIN ============
def login_view(request):
    if request.user.is_authenticated:
        try:
            perfil = request.user.perfil
            if perfil.tipo_perfil == 'gerente':
                return redirect('dashboard_gerente')
            elif perfil.tipo_perfil == 'chofer':
                return redirect('dashboard_chofer')
        except:
            pass
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            auth_login(request, user)
            
            try:
                perfil = user.perfil
                if perfil.tipo_perfil == 'gerente':
                    messages.success(request, f'Bienvenido Gerente {user.username}')
                    return redirect('dashboard_gerente')
                elif perfil.tipo_perfil == 'chofer':
                    messages.success(request, f'Bienvenido Chofer {user.username}')
                    return redirect('dashboard_chofer')
                else:
                    return redirect('inicio')
            except:
                return redirect('inicio')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos')
            return render(request, "login.html")
    
    return render(request, "login.html")

# ============ LOGOUT ============
def logout_view(request):
    auth_logout(request)
    messages.success(request, 'Sesión cerrada correctamente')
    return redirect('login')

# ================================================
# DASHBOARD GERENTE
# ================================================
@login_required
@user_passes_test(es_gerente, login_url='login')
def dashboard_gerente(request):
    hoy = datetime.now().date()
    alertas_vencimiento = []
    
    vehiculos = Vehiculo.objects.all()
    for v in vehiculos:
        if v.fecha_vencimiento_seguro:
            dias = (v.fecha_vencimiento_seguro - hoy).days
            if dias <= 30:
                alertas_vencimiento.append({
                    'vehiculo': v.placa,
                    'tipo': 'Seguro',
                    'fecha': v.fecha_vencimiento_seguro,
                    'dias': dias
                })
        
        if v.fecha_vencimiento_soat:
            dias = (v.fecha_vencimiento_soat - hoy).days
            if dias <= 30:
                alertas_vencimiento.append({
                    'vehiculo': v.placa,
                    'tipo': 'SOAT',
                    'fecha': v.fecha_vencimiento_soat,
                    'dias': dias
                })
    
    mantenimientos_pendientes = Mantenimiento.objects.filter(estado='pendiente').select_related('vehiculo')
    
    costos_vehiculos = []
    for v in vehiculos:
        total = Mantenimiento.objects.filter(vehiculo=v).aggregate(Sum('costo_taller'))['costo_taller__sum'] or 0
        if total > 0:
            costos_vehiculos.append({
                'vehiculo': v.placa,
                'total': total,
                'tipo': v.tipo_vehiculo
            })
    
    context = {
        'alertas_vencimiento': alertas_vencimiento,
        'mantenimientos_pendientes': mantenimientos_pendientes,
        'costos_vehiculos': costos_vehiculos,
        'total_vehiculos': vehiculos.count(),
        'total_mantenimientos': Mantenimiento.objects.count(),
        'total_costos': Mantenimiento.objects.aggregate(Sum('costo_taller'))['costo_taller__sum'] or 0,
    }
    return render(request, "dashboard_gerente.html", context)

# ================================================
# DASHBOARD CHOFER
# ================================================
@login_required
@user_passes_test(es_chofer, login_url='login')
def dashboard_chofer(request):
    perfil = request.user.perfil
    mis_vehiculos = Vehiculo.objects.filter(asignado_a=perfil)
    mis_reportes = ReporteFalla.objects.filter(chofer=perfil).order_by('-fecha_reporte')
    
    context = {
        'mis_vehiculos': mis_vehiculos,
        'mis_reportes': mis_reportes,
        'total_reportes': mis_reportes.count(),
    }
    return render(request, "dashboard_chofer.html", context)

# ================================================
# REPORTE DE FALLAS (CHOFER)
# ================================================
@login_required
@user_passes_test(es_chofer, login_url='login')
def nuevo_reporte_falla(request):
    perfil = request.user.perfil
    vehiculos = Vehiculo.objects.filter(asignado_a=perfil)

    if request.method == 'POST':
        vehiculo_id = request.POST.get('vehiculo')
        titulo = request.POST.get('titulo')
        descripcion = request.POST.get('descripcion')
        gravedad = request.POST.get('gravedad')
        foto = request.FILES.get('foto')
        archivo = request.FILES.get('archivo_adjunto')

        if not vehiculo_id:
            messages.error(request, "Debe seleccionar un vehículo")
            return render(request, "nuevo_reporte_falla.html", {'vehiculos': vehiculos})

        try:
            vehiculo_id = int(vehiculo_id)
        except ValueError:
            messages.error(request, "Vehículo inválido")
            return render(request, "nuevo_reporte_falla.html", {'vehiculos': vehiculos})

        vehiculo = get_object_or_404(
            Vehiculo,
            id=vehiculo_id,
            asignado_a=perfil
        )

        reporte = ReporteFalla(
            vehiculo=vehiculo,
            chofer=perfil,
            titulo=titulo,
            descripcion=descripcion,
            gravedad=gravedad,
            foto=foto,
            archivo_adjunto=archivo
        )
        reporte.save()

        messages.success(request, 'Reporte de falla guardado correctamente')
        return redirect('dashboard_chofer')

    return render(request, "nuevo_reporte_falla.html", {'vehiculos': vehiculos})

# ================================================
# APROBAR REPARACIONES (GERENTE)
# ================================================
@login_required
@user_passes_test(es_gerente, login_url='login')
def aprobar_reparacion(request, id):
    mantenimiento = get_object_or_404(Mantenimiento, id=id)
    
    if request.method == 'POST':
        accion = request.POST.get('accion')
        observaciones = request.POST.get('observaciones', '')
        
        if accion == 'aprobar':
            mantenimiento.estado = 'aprobado'
            mantenimiento.aprobado_por = request.user.perfil
            mantenimiento.fecha_aprobacion = datetime.now()
            mantenimiento.observaciones_gerente = observaciones
            messages.success(request, 'Mantenimiento aprobado correctamente')
        else:
            mantenimiento.estado = 'rechazado'
            mantenimiento.observaciones_gerente = observaciones
            messages.warning(request, 'Mantenimiento rechazado')
        
        mantenimiento.save()
        return redirect('dashboard_gerente')
    
    return render(request, "aprobar_reparacion.html", {'mantenimiento': mantenimiento})

# ================================================
# REPORTE DE COSTOS (GERENTE)
# ================================================
@login_required
@user_passes_test(es_gerente, login_url='login')
def reporte_costos(request):
    costos = Mantenimiento.objects.all().select_related('vehiculo')
    total_general = costos.aggregate(Sum('costo_taller'))['costo_taller__sum'] or 0
    
    resumen_vehiculos = []
    for v in Vehiculo.objects.all():
        total = Mantenimiento.objects.filter(vehiculo=v).aggregate(Sum('costo_taller'))['costo_taller__sum'] or 0
        if total > 0:
            resumen_vehiculos.append({
                'vehiculo': v.placa,
                'tipo': v.tipo_vehiculo,
                'total': total
            })
    
    context = {
        'costos': costos.order_by('-fecha_servicio'),
        'total_general': total_general,
        'resumen_vehiculos': resumen_vehiculos,
        'vehiculos': Vehiculo.objects.all(),
    }
    return render(request, "reporte_costos.html", context)

# ================================================
# VISTAS EXISTENTES DE VEHÍCULOS Y MANTENIMIENTOS
# ================================================
def nuevoVehiculo(request):
    if not request.user.is_authenticated or not es_gerente(request.user):
        return redirect('login')
    return render(request, "nuevoVehiculo.html")

def guardarVehiculo(request):
    if not request.user.is_authenticated or not es_gerente(request.user):
        return redirect('login')
    
    if request.method == 'POST':
        foto = request.FILES.get('foto')
        placa = request.POST.get('placa')
        tipo_vehiculo = request.POST.get('tipo_vehiculo')
        tipo_combustible = request.POST.get('tipo_combustible')
        seguro_vigente = request.POST.get('seguro_vigente') == 'on'
        anio_modelo = request.POST.get('anio_modelo')
        fecha_vencimiento_seguro = request.POST.get('fecha_vencimiento_seguro')
        fecha_vencimiento_soat = request.POST.get('fecha_vencimiento_soat')
        
        vehiculo = Vehiculo(
            foto=foto,
            placa=placa,
            tipo_vehiculo=tipo_vehiculo,
            tipo_combustible=tipo_combustible,
            seguro_vigente=seguro_vigente,
            anio_modelo=anio_modelo,
            fecha_vencimiento_seguro=fecha_vencimiento_seguro if fecha_vencimiento_seguro else None,
            fecha_vencimiento_soat=fecha_vencimiento_soat if fecha_vencimiento_soat else None
        )
        vehiculo.save()
        messages.success(request, 'Vehículo guardado correctamente.')
        return redirect('listado_vehiculos')
    return redirect('listado_vehiculos')

def listadoVehiculos(request):
    if not request.user.is_authenticated or not es_gerente(request.user):
        return redirect('login')
    vehiculos = Vehiculo.objects.all()
    return render(request, "listadoVehiculos.html", {"misvehiculos": vehiculos})

def eliminarVehiculo(request, id):
    if not request.user.is_authenticated or not es_gerente(request.user):
        return redirect('login')
    vehiculoEliminar = Vehiculo.objects.get(id=id)
    if vehiculoEliminar.foto:
        vehiculoEliminar.foto.delete()
    vehiculoEliminar.delete()
    messages.success(request, 'Vehículo eliminado correctamente.')
    return redirect('listado_vehiculos')

def editarVehiculos(request, id):
    if not request.user.is_authenticated or not es_gerente(request.user):
        return redirect('login')
    vehiculoEditar = Vehiculo.objects.get(id=id)
    return render(request, 'editarVehiculos.html', {'vehiculo': vehiculoEditar})

def procesarActualizacionVehiculo(request):
    if not request.user.is_authenticated or not es_gerente(request.user):
        return redirect('login')
    
    if request.method == 'POST':
        id = request.POST.get('id')
        placa = request.POST.get('placa')
        tipo_vehiculo = request.POST.get('tipo_vehiculo')
        tipo_combustible = request.POST.get('tipo_combustible')
        seguro_vigente = request.POST.get('seguro_vigente') == 'on'
        anio_modelo = request.POST.get('anio_modelo')
        
        vehiculoEditar = Vehiculo.objects.get(id=id)
        
        vehiculoEditar.placa = placa
        vehiculoEditar.tipo_vehiculo = tipo_vehiculo
        vehiculoEditar.tipo_combustible = tipo_combustible
        vehiculoEditar.seguro_vigente = seguro_vigente
        vehiculoEditar.anio_modelo = anio_modelo
        vehiculoEditar.fecha_vencimiento_seguro = request.POST.get('fecha_vencimiento_seguro') or None
        vehiculoEditar.fecha_vencimiento_soat = request.POST.get('fecha_vencimiento_soat') or None
        
        nueva_foto = request.FILES.get('foto')
        if nueva_foto:
            if vehiculoEditar.foto:
                import os
                if os.path.isfile(vehiculoEditar.foto.path):
                    os.remove(vehiculoEditar.foto.path)
            vehiculoEditar.foto = nueva_foto
        
        vehiculoEditar.save()
        messages.success(request, 'Vehículo actualizado correctamente.')
        return redirect('listado_vehiculos')
    return redirect('listado_vehiculos')

def nuevoMantenimiento(request):
    if not request.user.is_authenticated or not es_gerente(request.user):
        return redirect('login')
    vehiculos = Vehiculo.objects.all()
    return render(request, "nuevoMantenimiento.html", {"vehiculos": vehiculos})

def guardarMantenimiento(request):
    if not request.user.is_authenticated or not es_gerente(request.user):
        return redirect('login')
    
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
            repuestos_cambiados=repuestos_cambiados,
            estado='pendiente'
        )
        mantenimiento.save()
        messages.success(request, 'Mantenimiento guardado correctamente')
        return redirect('listado_mantenimientos')
    return redirect('listado_mantenimientos')

def listadoMantenimientos(request):
    if not request.user.is_authenticated or not es_gerente(request.user):
        return redirect('login')
    
    mantenimientos = Mantenimiento.objects.all()
    anio_actual = datetime.now().year
    vehiculos = Vehiculo.objects.all()
    PRESUPUESTO_LIMITE = Decimal(1000.00)
    
    autos_excedidos = []
    for auto in vehiculos:
        gasto_anual = Mantenimiento.objects.filter(
            vehiculo=auto, 
            fecha_servicio__year=anio_actual
        ).aggregate(Sum('costo_taller'))['costo_taller__sum'] or 0
        
        auto.total_mantenimiento = gasto_anual
        
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