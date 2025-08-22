#!/usr/bin/env python
"""
Script para gestionar la base de datos del proyecto FormoKaizen
Incluye comandos para crear migraciones, migrar y cargar datos iniciales
"""
import os
import sys
import django
from django.core.management import execute_from_command_line
from django.db import connection

def setup_django():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'formokaizen_backend.settings')
    django.setup()

def create_migrations():
    """Crear migraciones para todas las apps"""
    print("Creando migraciones...")
    execute_from_command_line(['manage.py', 'makemigrations', 'users'])
    execute_from_command_line(['manage.py', 'makemigrations', 'categories'])
    execute_from_command_line(['manage.py', 'makemigrations', 'tarjetas'])
    execute_from_command_line(['manage.py', 'makemigrations', 'teams'])
    execute_from_command_line(['manage.py', 'makemigrations', 'notifications'])

def migrate_database():
    """Ejecutar migraciones"""
    print("Ejecutando migraciones...")
    execute_from_command_line(['manage.py', 'migrate'])

def create_superuser():
    """Crear superusuario"""
    print("Creando superusuario...")
    from apps.users.models import User
    
    if not User.objects.filter(is_superuser=True).exists():
        User.objects.create_superuser(
            username='admin',
            email='admin@formokaizen.com',
            password='admin123',
            first_name='Administrador',
            last_name='Sistema',
            role='admin'
        )
        print("Superusuario creado: admin@formokaizen.com / admin123")
    else:
        print("Ya existe un superusuario")

def load_sample_data():
    """Cargar datos de ejemplo"""
    print("Cargando datos de ejemplo...")
    
    from apps.users.models import User
    from apps.categories.models import Category, WorkArea
    from apps.teams.models import Team, TeamMembership
    from apps.tarjetas.models import TarjetaRoja
    
    # Crear usuarios de ejemplo
    users_data = [
        {
            'username': 'juan.perez', 'email': 'juan.perez@empresa.com',
            'first_name': 'Juan', 'last_name': 'Pérez', 'role': 'supervisor',
            'department': 'Ingeniería', 'position': 'Supervisor de Producción'
        },
        {
            'username': 'maria.garcia', 'email': 'maria.garcia@empresa.com',
            'first_name': 'María', 'last_name': 'García', 'role': 'user',
            'department': 'Electrónica', 'position': 'Técnico Electrónico'
        },
        {
            'username': 'carlos.rodriguez', 'email': 'carlos.rodriguez@empresa.com',
            'first_name': 'Carlos', 'last_name': 'Rodríguez', 'role': 'user',
            'department': 'Soldadura', 'position': 'Soldador Especializado'
        },
        {
            'username': 'ana.martinez', 'email': 'ana.martinez@empresa.com',
            'first_name': 'Ana', 'last_name': 'Martínez', 'role': 'user',
            'department': 'Oficina', 'position': 'Analista de Calidad'
        }
    ]
    
    created_users = []
    for user_data in users_data:
        user, created = User.objects.get_or_create(
            username=user_data['username'],
            defaults={**user_data, 'password': 'pbkdf2_sha256$600000$dummy$dummy'}
        )
        if created:
            user.set_password('password123')
            user.save()
        created_users.append(user)
    
    # Crear categorías
    categories_data = [
        {
            'name': 'Electrónicos',
            'description': 'Equipos y componentes electrónicos',
            'color': '#2196F3',
            'icon': 'electronics'
        },
        {
            'name': 'Oficina',
            'description': 'Espacios de oficina y administrativos',
            'color': '#4CAF50',
            'icon': 'office'
        },
        {
            'name': 'Soldadura',
            'description': 'Estación de soldadura y equipos relacionados',
            'color': '#FF9800',
            'icon': 'welding'
        },
        {
            'name': 'Laboratorio',
            'description': 'Equipos de laboratorio y pruebas',
            'color': '#9C27B0',
            'icon': 'science'
        }
    ]
    
    admin_user = User.objects.filter(role='admin').first()
    created_categories = []
    
    for cat_data in categories_data:
        category, created = Category.objects.get_or_create(
            name=cat_data['name'],
            defaults={**cat_data, 'created_by': admin_user}
        )
        created_categories.append(category)
        
        # Crear áreas de trabajo para cada categoría
        if category.name == 'Electrónicos':
            work_areas = ['Banco de Pruebas', 'Almacén de Componentes', 'Reparaciones']
        elif category.name == 'Oficina':
            work_areas = ['Área Administrativa', 'Sala de Reuniones', 'Recepción']
        elif category.name == 'Soldadura':
            work_areas = ['Estación Principal', 'Área de Preparación', 'Control de Calidad']
        else:  # Laboratorio
            work_areas = ['Banco de Medición', 'Área de Calibración', 'Almacén de Instrumentos']
        
        for area_name in work_areas:
            WorkArea.objects.get_or_create(
                name=area_name,
                category=category,
                defaults={'description': f'Área de {area_name} en {category.name}'}
            )
    
    # Crear equipo de ejemplo
    if created_users:
        team, created = Team.objects.get_or_create(
            name='Equipo de Mejora Continua',
            defaults={
                'description': 'Equipo encargado de implementar mejoras en los procesos',
                'leader': created_users[0],  # Juan como líder
                'created_by': admin_user
            }
        )
        
        if created:
            for user in created_users:
                TeamMembership.objects.get_or_create(
                    team=team,
                    user=user,
                    defaults={
                        'role': 'coordinator' if user == created_users[0] else 'member',
                        'added_by': admin_user
                    }
                )
    
    # Crear tarjetas rojas de ejemplo
    if created_categories and created_users:
        sample_tarjetas = [
            {
                'numero': 'TR-001',
                'descripcion': 'Problema de ventilación en estación de soldadura - El sistema de extracción de humos no está funcionando correctamente',
                'category': next(c for c in created_categories if c.name == 'Soldadura'),
                'priority': 'high',
                'status': 'open',
                'razon_motivo': 'Falta de mantenimiento del sistema de ventilación',
                'destino_final': 'Revisar y limpiar los filtros del sistema de extracción',
                'sector': 'Soldadura',
                'quien_lo_hizo': 'Carlos Rodríguez',
                'created_by': created_users[2] if len(created_users) > 2 else created_users[0]
            },
            {
                'numero': 'TR-002',
                'descripcion': 'Componentes defectuosos en lote de resistencias - Se encontraron múltiples resistencias con valores fuera de especificación',
                'category': next(c for c in created_categories if c.name == 'Electrónicos'),
                'priority': 'medium',
                'status': 'in_progress',
                'razon_motivo': 'Posible problema en el lote del proveedor',
                'destino_final': 'Contactar al proveedor y establecer controles adicionales',
                'sector': 'Electrónicos',
                'quien_lo_hizo': 'María García',
                'created_by': created_users[1] if len(created_users) > 1 else created_users[0]
            }
        ]
        
        for tarjeta_data in sample_tarjetas:
            TarjetaRoja.objects.get_or_create(
                numero=tarjeta_data['numero'],
                defaults=tarjeta_data
            )
    
    print("Datos de ejemplo cargados exitosamente")

def reset_database():
    """Resetear completamente la base de datos"""
    print("ADVERTENCIA: Esto eliminará TODOS los datos de la base de datos")
    confirm = input("¿Estás seguro? Escribe 'CONFIRMAR' para continuar: ")
    
    if confirm == 'CONFIRMAR':
        print("Eliminando todas las tablas...")
        
        with connection.cursor() as cursor:
            cursor.execute("""
                DROP SCHEMA public CASCADE;
                CREATE SCHEMA public;
                GRANT ALL ON SCHEMA public TO postgres;
                GRANT ALL ON SCHEMA public TO public;
            """)
        
        print("Base de datos reseteada. Ejecutando setup completo...")
        create_migrations()
        migrate_database()
        create_superuser()
        load_sample_data()
    else:
        print("Operación cancelada")

def main():
    setup_django()
    
    if len(sys.argv) < 2:
        print("Uso: python manage_db.py [comando]")
        print("Comandos disponibles:")
        print("  setup - Configuración completa inicial")
        print("  migrate - Solo ejecutar migraciones")
        print("  sample_data - Cargar datos de ejemplo")
        print("  superuser - Crear superusuario")
        print("  reset - Resetear base de datos (¡PELIGROSO!)")
        return
    
    command = sys.argv[1]
    
    if command == 'setup':
        create_migrations()
        migrate_database()
        create_superuser()
        load_sample_data()
        print("\n🎉 Setup completo! El backend está listo para usar.")
        print("📍 Panel de admin: http://localhost:8000/admin/")
        print("🔑 Credenciales: admin@formokaizen.com / admin123")
        
    elif command == 'migrate':
        migrate_database()
        
    elif command == 'sample_data':
        load_sample_data()
        
    elif command == 'superuser':
        create_superuser()
        
    elif command == 'reset':
        reset_database()
        
    else:
        print(f"Comando desconocido: {command}")

if __name__ == '__main__':
    main()