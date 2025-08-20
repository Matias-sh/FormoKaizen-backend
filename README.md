# FormoKaizen Backend

Sistema backend para la aplicación FormoKaizen - Gestión de Tarjetas Rojas para mejora continua en oficinas de ingeniería.

## 🚀 Características Principales

- **Autenticación JWT** con roles de usuario (Admin, Supervisor, Usuario)
- **Gestión de Tarjetas Rojas** con workflow completo de aprobación
- **Sistema de Categorías flexible** para diferentes espacios de trabajo
- **Trabajo en equipo** con asignación de proyectos
- **Notificaciones automáticas** con preferencias personalizables
- **API REST completa** con documentación OpenAPI
- **Panel de administración** de Django
- **Base de datos PostgreSQL**
- **Cache con Redis**
- **Procesamiento asíncrono** con Celery

## 🏗️ Arquitectura

```
├── formokaizen_backend/     # Configuración principal
├── apps/
│   ├── users/              # Gestión de usuarios y autenticación
│   ├── categories/         # Categorías y áreas de trabajo
│   ├── tarjetas/          # Tarjetas rojas y workflow
│   ├── teams/             # Equipos y proyectos colaborativos
│   └── notifications/     # Sistema de notificaciones
├── fixtures/              # Datos iniciales
└── media/                # Archivos subidos
```

## 📋 Requisitos

- Python 3.11+
- PostgreSQL 13+
- Redis 6+
- Docker (opcional)

## 🚀 Instalación Rápida con Docker

```bash
# Clonar repositorio
cd backend

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus configuraciones

# Levantar servicios
docker-compose up -d

# Setup inicial de la base de datos
docker-compose exec django python manage_db.py setup
```

## 🔧 Instalación Manual

```bash
# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# o venv\Scripts\activate  # Windows

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus configuraciones

# Configurar base de datos PostgreSQL
createdb formokaizen

# Setup inicial
python manage_db.py setup
```

## 🎯 Datos Iniciales

El script de setup crea automáticamente:

### Usuarios de ejemplo:
- **Admin**: admin@formokaizen.com / admin123
- **Supervisor**: juan.perez@empresa.com / password123
- **Técnico**: maria.garcia@empresa.com / password123
- **Soldador**: carlos.rodriguez@empresa.com / password123
- **Analista**: ana.martinez@empresa.com / password123

### Categorías configuradas:
- **Electrónicos** (Banco de Pruebas, Almacén de Componentes)
- **Oficina** (Área Administrativa, Sala de Reuniones)
- **Soldadura** (Estación Principal, Área de Preparación)
- **Laboratorio** (Banco de Medición, Área de Calibración)

## 🔌 API Endpoints

### Autenticación
```
POST /api/auth/login/          # Iniciar sesión
POST /api/auth/register/       # Registro de usuario
GET  /api/auth/profile/        # Perfil del usuario
PUT  /api/auth/profile/update/ # Actualizar perfil
```

### Tarjetas Rojas
```
GET  /api/tarjetas/                    # Listar tarjetas (con filtros)
POST /api/tarjetas/                    # Crear tarjeta
GET  /api/tarjetas/{id}/               # Detalle de tarjeta
PUT  /api/tarjetas/{id}/               # Actualizar tarjeta
POST /api/tarjetas/{id}/approve/       # Aprobar/Rechazar tarjeta
POST /api/tarjetas/{id}/upload-image/  # Subir imagen
POST /api/tarjetas/{id}/add-comment/   # Agregar comentario
GET  /api/tarjetas/dashboard/stats/    # Estadísticas
```

### Categorías y Áreas
```
GET  /api/categories/                           # Listar categorías
POST /api/categories/                           # Crear categoría
GET  /api/categories/{id}/work-areas/           # Áreas de trabajo
POST /api/categories/{id}/work-areas/           # Crear área
```

### Equipos
```
GET  /api/teams/                        # Listar equipos
POST /api/teams/                        # Crear equipo
GET  /api/teams/{id}/                   # Detalle de equipo
POST /api/teams/{id}/add-member/        # Agregar miembro
GET  /api/teams/{id}/projects/          # Proyectos del equipo
```

### Notificaciones
```
GET  /api/notifications/                # Listar notificaciones
PUT  /api/notifications/{id}/read/      # Marcar como leída
PUT  /api/notifications/mark-all-read/  # Marcar todas como leídas
GET  /api/notifications/preferences/    # Preferencias
PUT  /api/notifications/preferences/    # Actualizar preferencias
```

## 🔍 Filtros de API

### Tarjetas Rojas
```
GET /api/tarjetas/?status=open&priority=high&category=1
GET /api/tarjetas/?assigned_to=me&search=soldadura
GET /api/tarjetas/?created_by=5&page=2&per_page=10
```

### Notificaciones
```
GET /api/notifications/?unread_only=true&type=tarjeta_assigned
```

## 🛡️ Permisos y Roles

### Usuario Regular
- Crear tarjetas rojas (requieren aprobación)
- Ver y comentar sus tarjetas
- Ver equipos donde participa
- Recibir notificaciones

### Supervisor
- Aprobar/rechazar tarjetas
- Crear y gestionar equipos
- Ver todas las tarjetas
- Crear categorías y áreas
- Acceso a estadísticas básicas

### Administrador
- Acceso completo al sistema
- Gestión de usuarios
- Panel de administración
- Estadísticas avanzadas
- Configuración del sistema

## 🔧 Comandos Útiles

```bash
# Setup completo inicial
python manage_db.py setup

# Solo migraciones
python manage_db.py migrate

# Solo datos de ejemplo
python manage_db.py sample_data

# Crear superusuario
python manage_db.py superuser

# Resetear base de datos (¡CUIDADO!)
python manage_db.py reset

# Servidor de desarrollo
python manage.py runserver

# Tests
python manage.py test

# Crear migraciones
python manage.py makemigrations

# Shell de Django
python manage.py shell
```

## 📊 Panel de Administración

Accede a `http://localhost:8000/admin/` con las credenciales del administrador.

Funcionalidades disponibles:
- Gestión completa de usuarios
- Visualización de tarjetas rojas
- Configuración de categorías
- Administración de equipos
- Sistema de notificaciones
- Estadísticas y reportes

## 🐳 Desarrollo con Docker

```bash
# Levantar solo la base de datos
docker-compose up postgres redis -d

# Ver logs
docker-compose logs -f django

# Ejecutar comandos en el contenedor
docker-compose exec django python manage.py shell
docker-compose exec django python manage_db.py sample_data

# Parar servicios
docker-compose down
```

## 🔐 Configuración de Producción

Para producción, asegúrate de:

1. Configurar `DEBUG=False`
2. Usar una `SECRET_KEY` segura
3. Configurar `ALLOWED_HOSTS` correctamente
4. Usar variables de entorno para credenciales
5. Configurar HTTPS
6. Usar un servidor web (nginx) como proxy
7. Configurar backups de la base de datos

## 🤝 Contribución

1. Fork del proyecto
2. Crear rama feature (`git checkout -b feature/AmazingFeature`)
3. Commit cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir Pull Request

## 📝 Notas de Desarrollo

- El primer usuario registrado automáticamente se convierte en admin
- Las notificaciones se crean automáticamente via signals de Django
- Los archivos de imagen se almacenan en el directorio `media/`
- Se incluyen fixtures con datos iniciales para desarrollo
- El sistema está preparado para notificaciones push (requiere configuración adicional)

## 📞 Soporte

Para soporte técnico o preguntas sobre la implementación, contacta al equipo de desarrollo.