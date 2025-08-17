# Routes App - Gestión de Trayectos

Aplicación FastAPI para la gestión de trayectos/rutas en el sistema de entregas.

## 📁 Estructura del Proyecto

```
routes_app/
├── app/                    # Código fuente de la aplicación
│   ├── main.py            # Punto de entrada FastAPI
│   ├── api.py             # Endpoints y lógica de negocio
│   ├── db.py              # Conexión y esquema de base de datos
│   └── __init__.py        # Package marker
├── tests/                 # Pruebas unitarias
│   └── test_routes_api.py # Tests de la API
├── k8s/                   # Archivos de despliegue Kubernetes
│   ├── routes-app-deployment.yml  # Deployment de la app
│   ├── routes-db-deployment.yml   # Deployment de PostgreSQL
│   └── routes-netpol.yml         # Network Policy
├── dockerfile             # Imagen Docker
├── pyproject.toml        # Dependencias Python (Poetry)
└── README.md             # Documentación específica
```

## 🚀 Despliegue

### Kubernetes
```bash
# Aplicar todos los recursos
kubectl apply -f k8s/

# Verificar despliegue
kubectl get pods -l app=routes-app
kubectl get services routes-app-service
```

### Docker
```bash
# Construir imagen
docker build -t routes-app:latest routes_app/

# Ejecutar localmente
docker run -p 8002:8000 routes-app:latest
```

## 📖 API Endpoints

- `GET /ping` - Health check
- `GET /routes/ping` - Health check específico
- `POST /routes/reset` - Reset base de datos
- `POST /routes` - Crear trayecto
- `GET /routes` - Listar trayectos
- `GET /routes/{route_id}` - Obtener trayecto
- `PUT /routes/{route_id}` - Actualizar trayecto
- `DELETE /routes/{route_id}` - Eliminar trayecto
- `GET /routes/count` - Contar trayectos
- `GET /routes?flight={flightId}` - Buscar por vuelo

## 🔧 Desarrollo

Consultar `routes_app/README.md` para instrucciones detalladas de desarrollo, testing y configuración.

## 🏗️ Arquitectura

Esta aplicación es parte de un sistema distribuido de microservicios para gestión de entregas y trayectos.
