# API Documentation - FormoKaizen Backend

## Base URL
```
http://localhost:8000/api/
```

## Autenticación

### 1. Registro de Usuario
**Endpoint:** `POST /auth/register/`

**Body:**
```json
{
    "username": "usuario123",
    "email": "usuario@ejemplo.com",
    "password": "contraseña123",
    "first_name": "Juan",
    "last_name": "Pérez",
    "employee_id": "EMP001",
    "phone": "123456789",
    "department": "Producción",
    "position": "Operario"
}
```

**Response (201):**
```json
{
    "message": "Usuario creado exitosamente",
    "user": {
        "id": 1,
        "username": "usuario123",
        "email": "usuario@ejemplo.com",
        "first_name": "Juan",
        "last_name": "Pérez",
        "role": "user",
        "employee_id": "EMP001",
        "phone": "123456789",
        "department": "Producción",
        "position": "Operario"
    },
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### 2. Login
**Endpoint:** `POST /auth/login/`

**Body:**
```json
{
    "email": "usuario@ejemplo.com",
    "password": "contraseña123"
}
```

**Response (200):**
```json
{
    "user": {
        "id": 1,
        "username": "usuario123",
        "email": "usuario@ejemplo.com",
        "first_name": "Juan",
        "last_name": "Pérez",
        "role": "user",
        "employee_id": "EMP001",
        "phone": "123456789",
        "department": "Producción",
        "position": "Operario"
    },
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### 3. Perfil de Usuario
**Endpoint:** `GET /auth/profile/`

**Headers:**
```
Authorization: Bearer {access_token}
```

**Response (200):**
```json
{
    "id": 1,
    "username": "usuario123",
    "email": "usuario@ejemplo.com",
    "first_name": "Juan",
    "last_name": "Pérez",
    "role": "user",
    "employee_id": "EMP001",
    "phone": "123456789",
    "department": "Producción",
    "position": "Operario"
}
```

## Tarjetas Rojas

### 1. Listar Tarjetas
**Endpoint:** `GET /tarjetas/`

**Headers:**
```
Authorization: Bearer {access_token}
```

**Query Parameters (opcionales):**
- `status`: Filtrar por estado (open, pending_approval, approved, in_progress, resolved, closed, rejected)
- `priority`: Filtrar por prioridad (low, medium, high, critical)
- `sector`: Filtrar por sector
- `assigned_to`: Filtrar por usuario asignado (usar 'me' para tarjetas asignadas al usuario actual)
- `created_by`: Filtrar por creador (usar 'me' para tarjetas creadas por el usuario actual)
- `search`: Buscar en número, descripción, sector, o quién lo hizo
- `page`: Número de página (default: 1)
- `per_page`: Elementos por página (default: 20)

**Response (200):**
```json
{
    "results": [
        {
            "id": 1,
            "code": "TR-0001",
            "numero": "TR-2024-001",
            "fecha": "2024-08-20",
            "sector": "Producción",
            "descripcion": "Problema con máquina empacadora",
            "status": "open",
            "priority": "high",
            "created_by": {
                "id": 1,
                "username": "usuario123",
                "email": "usuario@ejemplo.com",
                "first_name": "Juan",
                "last_name": "Pérez"
            },
            "assigned_to": null,
            "approved_by": null,
            "quien_lo_hizo": "Juan Pérez",
            "created_at": "2024-08-20T10:30:00.000000Z",
            "updated_at": "2024-08-20T10:30:00.000000Z",
            "is_overdue": false,
            "days_open": 1
        }
    ],
    "count": 25,
    "page": 1,
    "per_page": 20,
    "total_pages": 2
}
```

### 2. Crear Tarjeta
**Endpoint:** `POST /tarjetas/`

**Headers:**
```
Authorization: Bearer {access_token}
Content-Type: application/json
```

**Body:**
```json
{
    "numero": "TR-2024-002",
    "fecha": "2024-08-20",
    "sector": "Mantenimiento",
    "descripcion": "Fuga de aceite en compresor principal",
    "razon_motivo": "Falta de mantenimiento preventivo en sellos",
    "quien_lo_hizo": "Carlos Rodríguez",
    "destino_final": "Reemplazar sellos y implementar programa de mantenimiento",
    "fecha_final": "2024-08-25",
    "priority": "critical"
}
```

**Response (201):**
```json
{
    "id": 2,
    "code": "TR-0002",
    "numero": "TR-2024-002",
    "fecha": "2024-08-20",
    "sector": "Mantenimiento",
    "descripcion": "Fuga de aceite en compresor principal",
    "razon_motivo": "Falta de mantenimiento preventivo en sellos",
    "quien_lo_hizo": "Carlos Rodríguez",
    "destino_final": "Reemplazar sellos y implementar programa de mantenimiento",
    "fecha_final": "2024-08-25",
    "status": "pending_approval",
    "priority": "critical",
    "created_by": {
        "id": 1,
        "username": "usuario123",
        "email": "usuario@ejemplo.com",
        "first_name": "Juan",
        "last_name": "Pérez"
    },
    "assigned_to": null,
    "approved_by": null,
    "resolution_notes": "",
    "images": [],
    "comments": [],
    "history": [],
    "created_at": "2024-08-20T11:15:00.000000Z",
    "updated_at": "2024-08-20T11:15:00.000000Z",
    "approved_at": null,
    "closed_at": null,
    "is_overdue": false,
    "days_open": 0
}
```

### 3. Ver Detalle de Tarjeta
**Endpoint:** `GET /tarjetas/{id}/`

**Headers:**
```
Authorization: Bearer {access_token}
```

**Response (200):**
```json
{
    "id": 1,
    "code": "TR-0001",
    "numero": "TR-2024-001",
    "fecha": "2024-08-20",
    "sector": "Producción",
    "descripcion": "Problema con máquina empacadora",
    "razon_motivo": "Desgaste de rodamientos por uso continuo",
    "quien_lo_hizo": "Juan Pérez",
    "destino_final": "Reemplazar rodamientos y ajustar programación de mantenimiento",
    "fecha_final": "2024-08-25",
    "status": "in_progress",
    "priority": "high",
    "created_by": {
        "id": 1,
        "username": "usuario123",
        "email": "usuario@ejemplo.com",
        "first_name": "Juan",
        "last_name": "Pérez"
    },
    "assigned_to": {
        "id": 2,
        "username": "supervisor1",
        "email": "supervisor@ejemplo.com",
        "first_name": "María",
        "last_name": "García"
    },
    "approved_by": {
        "id": 2,
        "username": "supervisor1",
        "email": "supervisor@ejemplo.com",
        "first_name": "María",
        "last_name": "García"
    },
    "resolution_notes": "",
    "images": [
        {
            "id": 1,
            "image": "/media/tarjetas/2024/08/20/maquina_problema.jpg",
            "description": "Vista del problema en la máquina",
            "uploaded_by": {
                "id": 1,
                "username": "usuario123",
                "email": "usuario@ejemplo.com",
                "first_name": "Juan",
                "last_name": "Pérez"
            },
            "uploaded_at": "2024-08-20T10:35:00.000000Z"
        }
    ],
    "comments": [
        {
            "id": 1,
            "comment": "Se aprueba la tarjeta, procediendo con el mantenimiento",
            "is_internal": true,
            "user": {
                "id": 2,
                "username": "supervisor1",
                "email": "supervisor@ejemplo.com",
                "first_name": "María",
                "last_name": "García"
            },
            "created_at": "2024-08-20T11:00:00.000000Z"
        }
    ],
    "history": [
        {
            "id": 1,
            "action": "created",
            "old_value": "",
            "new_value": "pending_approval",
            "user": {
                "id": 1,
                "username": "usuario123",
                "email": "usuario@ejemplo.com",
                "first_name": "Juan",
                "last_name": "Pérez"
            },
            "timestamp": "2024-08-20T10:30:00.000000Z"
        },
        {
            "id": 2,
            "action": "approve",
            "old_value": "pending_approval",
            "new_value": "approved",
            "user": {
                "id": 2,
                "username": "supervisor1",
                "email": "supervisor@ejemplo.com",
                "first_name": "María",
                "last_name": "García"
            },
            "timestamp": "2024-08-20T11:00:00.000000Z"
        }
    ],
    "created_at": "2024-08-20T10:30:00.000000Z",
    "updated_at": "2024-08-20T11:00:00.000000Z",
    "approved_at": "2024-08-20T11:00:00.000000Z",
    "closed_at": null,
    "is_overdue": false,
    "days_open": 1
}
```

### 4. Actualizar Tarjeta
**Endpoint:** `PUT /tarjetas/{id}/`

**Headers:**
```
Authorization: Bearer {access_token}
Content-Type: application/json
```

**Body:**
```json
{
    "descripcion": "Problema con máquina empacadora - Actualizado",
    "razon_motivo": "Desgaste de rodamientos confirmado por inspección",
    "destino_final": "Reemplazar rodamientos completos y revisar alineación",
    "status": "in_progress",
    "priority": "critical",
    "fecha_final": "2024-08-30"
}
```

**Response (200):**
```json
{
    "id": 1,
    "code": "TR-0001",
    "numero": "TR-2024-001",
    "fecha": "2024-08-20",
    "sector": "Producción",
    "descripcion": "Problema con máquina empacadora - Actualizado",
    "razon_motivo": "Desgaste de rodamientos confirmado por inspección",
    "quien_lo_hizo": "Juan Pérez",
    "destino_final": "Reemplazar rodamientos completos y revisar alineación",
    "fecha_final": "2024-08-30",
    "status": "in_progress",
    "priority": "critical",
    "created_by": {...},
    "assigned_to": {...},
    "approved_by": {...},
    "resolution_notes": "",
    "images": [...],
    "comments": [...],
    "history": [...],
    "created_at": "2024-08-20T10:30:00.000000Z",
    "updated_at": "2024-08-20T12:00:00.000000Z",
    "approved_at": "2024-08-20T11:00:00.000000Z",
    "closed_at": null,
    "is_overdue": false,
    "days_open": 1
}
```

### 5. Eliminar Tarjeta
**Endpoint:** `DELETE /tarjetas/{id}/`

**Headers:**
```
Authorization: Bearer {access_token}
```

**Response (200):**
```json
{
    "message": "Tarjeta eliminada exitosamente"
}
```

### 6. Aprobar/Rechazar Tarjeta
**Endpoint:** `POST /tarjetas/{id}/approve/`

**Headers:**
```
Authorization: Bearer {access_token}
Content-Type: application/json
```

**Body:**
```json
{
    "action": "approve",
    "comment": "Se aprueba la intervención en la máquina"
}
```

**Response (200):**
```json
{
    "message": "Tarjeta aprobada exitosamente",
    "tarjeta": {
        "id": 1,
        "code": "TR-0001",
        "status": "approved",
        ...
    }
}
```

### 7. Subir Imagen a Tarjeta
**Endpoint:** `POST /tarjetas/{id}/upload-image/`

**Headers:**
```
Authorization: Bearer {access_token}
Content-Type: multipart/form-data
```

**Body (FormData):**
```
image: [archivo de imagen]
description: "Descripción de la imagen"
```

**Response (201):**
```json
{
    "id": 1,
    "image": "/media/tarjetas/2024/08/20/problema_maquina.jpg",
    "description": "Descripción de la imagen",
    "uploaded_by": {
        "id": 1,
        "username": "usuario123",
        "email": "usuario@ejemplo.com",
        "first_name": "Juan",
        "last_name": "Pérez"
    },
    "uploaded_at": "2024-08-20T10:35:00.000000Z"
}
```

### 8. Agregar Comentario a Tarjeta
**Endpoint:** `POST /tarjetas/{id}/add-comment/`

**Headers:**
```
Authorization: Bearer {access_token}
Content-Type: application/json
```

**Body:**
```json
{
    "comment": "Se está procediendo con la reparación",
    "is_internal": false
}
```

**Response (201):**
```json
{
    "id": 2,
    "comment": "Se está procediendo con la reparación",
    "is_internal": false,
    "user": {
        "id": 1,
        "username": "usuario123",
        "email": "usuario@ejemplo.com",
        "first_name": "Juan",
        "last_name": "Pérez"
    },
    "created_at": "2024-08-20T14:00:00.000000Z"
}
```

### 9. Estadísticas del Dashboard
**Endpoint:** `GET /tarjetas/dashboard-stats/`

**Headers:**
```
Authorization: Bearer {access_token}
```

**Response (200):**
```json
{
    "total_tarjetas": 45,
    "status_stats": {
        "open": 12,
        "pending_approval": 5,
        "in_progress": 15,
        "resolved": 10,
        "overdue": 3
    },
    "priority_stats": {
        "low": 8,
        "medium": 20,
        "high": 12,
        "critical": 5
    },
    "sector_stats": [
        {
            "sector": "Producción",
            "total": 18
        },
        {
            "sector": "Mantenimiento",
            "total": 12
        },
        {
            "sector": "Calidad",
            "total": 8
        },
        {
            "sector": "Logística",
            "total": 7
        }
    ]
}
```

## Estados de las Tarjetas

- `open`: Abierta
- `pending_approval`: Pendiente de Aprobación
- `approved`: Aprobada
- `in_progress`: En Progreso
- `resolved`: Resuelta
- `closed`: Cerrada
- `rejected`: Rechazada

## Niveles de Prioridad

- `low`: Baja
- `medium`: Media
- `high`: Alta
- `critical`: Crítica

## Códigos de Error Comunes

### 400 - Bad Request
```json
{
    "field_name": ["Error específico del campo"]
}
```

### 401 - Unauthorized
```json
{
    "error": "Credenciales inválidas"
}
```

### 403 - Forbidden
```json
{
    "error": "No tienes permisos para realizar esta acción"
}
```

### 404 - Not Found
```json
{
    "error": "Tarjeta no encontrada"
}
```

## Notas para Desarrolladores Android

1. **Autenticación**: Guarda el `access_token` y `refresh_token`. El access token tiene 24 horas de validez.

2. **Headers Requeridos**: 
   - Para todas las llamadas autenticadas: `Authorization: Bearer {access_token}`
   - Para envío de JSON: `Content-Type: application/json`
   - Para subida de archivos: `Content-Type: multipart/form-data`

3. **Formatos de Fecha**: 
   - Fechas se envían en formato `YYYY-MM-DD`
   - Timestamps se devuelven en formato ISO 8601

4. **Paginación**: Usa los parámetros `page` y `per_page` para controlar la paginación.

5. **Filtros**: Combina múltiples filtros en la URL para búsquedas específicas.

6. **Subida de Imágenes**: Soporta JPG, PNG, y otros formatos de imagen comunes.

## Comando para Iniciar el Servidor

```bash
cd C:\Users\Matias\Desktop\back-formokaizen
venv\Scripts\activate
python manage.py runserver 0.0.0.0:8000
```

El servidor estará disponible en `http://localhost:8000` o `http://tu-ip:8000`