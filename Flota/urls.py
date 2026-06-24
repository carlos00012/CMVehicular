from django.urls import path
from . import views

urlpatterns = [
    # Vistas principales
    path('', views.inicio, name='inicio'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # ============================================
    # PÁGINAS EXCLUSIVAS PARA GERENTE
    # ============================================
    path('dashboard/gerente/', views.dashboard_gerente, name='dashboard_gerente'),
    
    # Vehículos (Gerente)
    path('nuevoVehiculo/', views.nuevoVehiculo, name='nuevo_vehiculo'),
    path('guardarVehiculo/', views.guardarVehiculo, name='guardar_vehiculo'),
    path('listadoVehiculos/', views.listadoVehiculos, name='listado_vehiculos'),
    path('eliminarVehiculo/<id>', views.eliminarVehiculo, name='eliminar_vehiculo'),
    path('editarVehiculos/<id>', views.editarVehiculos, name='editar_vehiculos'),
    path('procesarActualizacionVehiculo/', views.procesarActualizacionVehiculo, name='procesar_actualizacion'),
    
    # Mantenimientos (Gerente)
    path('nuevoMantenimiento/', views.nuevoMantenimiento, name='nuevo_mantenimiento'),
    path('guardarMantenimiento/', views.guardarMantenimiento, name='guardar_mantenimiento'),
    path('listadoMantenimientos/', views.listadoMantenimientos, name='listado_mantenimientos'),
    
    # Aprobaciones (Gerente)
    path('aprobar/reparacion/<id>', views.aprobar_reparacion, name='aprobar_reparacion'),
    
    # Costos (Gerente)
    path('costos/reporte/', views.reporte_costos, name='reporte_costos'),
    
    # ============================================
    # PÁGINAS EXCLUSIVAS PARA CHOFER
    # ============================================
    path('dashboard/chofer/', views.dashboard_chofer, name='dashboard_chofer'),
    path('reporte/nuevo/', views.nuevo_reporte_falla, name='nuevo_reporte_falla'),
]