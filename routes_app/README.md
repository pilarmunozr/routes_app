# Routes App

API REST para la gestión de rutas/trayectos del sistema. Esta aplicación maneja la creación, consulta, actualización y eliminación de rutas de viaje.

## Estructura del Proyecto

```
routes_app/
├── app/
│   ├── __init__.py
│   ├── main.py          # Aplicación principal FastAPI
│   ├── api.py           # Endpoints y lógica de negocio
│   └── db.py            # Conexión y configuración de base de datos
├── tests/
│   └── test_routes_api.py # Pruebas unitarias
├── dockerfile           # Imagen Docker
├── pyproject.toml       # Dependencias y configuración Poetry
├── poetry.lock          # Versiones específicas de dependencias
└── README.md           # Este archivo
```

## Tecnologías

- **Framework**: FastAPI 0.111+
- **Base de datos**: PostgreSQL con psycopg2-binary
- **Validación**: Pydantic
- **Servidor**: Uvicorn
- **Pruebas**: pytest con coverage
- **Gestión de dependencias**: Poetry
- **Contenederización**: Docker

## Variables de Ambiente

| Variable      | Descripción                         | Valor por defecto   |
| ------------- | ----------------------------------- | ------------------- |
| `DB_HOST`     | Host de la base de datos PostgreSQL | `routes-db-service` |
| `DB_PORT`     | Puerto de la base de datos          | `5432`              |
| `DB_USER`     | Usuario de la base de datos         | `postgres`          |
| `DB_PASSWORD` | Contraseña de la base de datos      | `postgres`          |
| `DB_NAME`     | Nombre de la base de datos          | `routes_db`         |

## API Endpoints

### Públicos (sin autenticación)

- `GET /ping` - Health check de la aplicación
- `GET /routes/ping` - Health check específico de rutas
- `POST /reset` - Reinicia la base de datos (solo para desarrollo)
- `POST /routes/reset` - Reinicia la base de datos (endpoint alternativo)
- `POST /routes` - Crear nueva ruta
- `GET /routes` - Listar rutas (con paginación)
- `GET /routes/count` - Obtener número total de rutas
- `GET /routes/{route_id}` - Obtener información de una ruta específica
- `PATCH /routes/{route_id}` - Actualizar información de una ruta
- `DELETE /routes/{route_id}` - Eliminar una ruta

## Esquemas de Datos

### RouteCreate

```json
{
  "origin": "string (required)",
  "destination": "string (required)",
  "departure_date": "datetime ISO format (required)",
  "arrival_date": "datetime ISO format (required)",
  "capacity": "integer > 0 (required)",
  "description": "string (optional)"
}
```

### RouteUpdate

```json
{
  "origin": "string (optional)",
  "destination": "string (optional)",
  "departure_date": "datetime ISO format (optional)",
  "arrival_date": "datetime ISO format (optional)",
  "capacity": "integer > 0 (optional)",
  "description": "string (optional)"
}
```

## Modelo de Datos

### Route (Ruta/Trayecto)

| Campo            | Tipo      | Descripción                     |
| ---------------- | --------- | ------------------------------- |
| `id`             | UUID      | Identificador único de la ruta  |
| `origin`         | string    | Ciudad o lugar de origen        |
| `destination`    | string    | Ciudad o lugar de destino       |
| `departure_date` | timestamp | Fecha y hora de salida          |
| `arrival_date`   | timestamp | Fecha y hora de llegada         |
| `capacity`       | integer   | Capacidad máxima de pasajeros   |
| `description`    | string    | Descripción adicional del viaje |
| `created_at`     | timestamp | Fecha de creación del registro  |

## Validaciones

- La fecha de salida debe ser anterior a la fecha de llegada
- La capacidad debe ser mayor a 0
- Origen y destino son campos requeridos
- Fechas deben estar en formato ISO UTC

## Desarrollo Local

### Requisitos

- Python 3.11+
- Poetry
- PostgreSQL

### Instalación

```bash
# Navegar al directorio
cd routes_app

# Instalar dependencias
poetry install

# Configurar variables de ambiente
export DB_HOST=localhost
export DB_PORT=5432
export DB_USER=postgres
export DB_PASSWORD=postgres
export DB_NAME=routes_db

# Ejecutar aplicación
poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Pruebas

```bash
# Ejecutar todas las pruebas
poetry run pytest

# Ejecutar pruebas con cobertura
poetry run pytest --cov=app --cov-report=term-missing --cov-fail-under=70

# Ejecutar linters
poetry run ruff check .
poetry run black --check .
```

## Despliegue con Docker

### Construcción de la imagen

```bash
# Desde el directorio routes_app
docker build -t routes-app:v1.0.0 .
```

## Despliegue en Kubernetes

Los archivos de despliegue están en la carpeta `/k8s` del proyecto principal:

```bash
# Desplegar en Minikube
kubectl apply -f k8s/routes-db-deployment.yml
kubectl apply -f k8s/routes-app-deployment.yml
kubectl apply -f k8s/routes-netpol.yml

# Verificar estado
kubectl get pods
kubectl get services
```

## Testing

La aplicación incluye pruebas completas que cubren:

- ✅ Todos los endpoints CRUD
- ✅ Casos de éxito y error
- ✅ Validación de entrada (fechas, capacidad)
- ✅ Operaciones de paginación
- ✅ Ciclo completo CRUD
- ✅ Cobertura mínima del 70%

Para ejecutar las pruebas en CI/CD:

```bash
make unittest DIR=routes_app
```

## Notas de Desarrollo

- Las fechas se manejan en formato ISO UTC según restricciones del proyecto
- La aplicación usa volúmenes efímeros (emptyDir) según requisitos
- Los datos se reinician cuando el pod de base de datos se reinicia
- La base de datos se inicializa automáticamente al primer arranque
- Validación automática de orden de fechas (salida antes que llegada)
