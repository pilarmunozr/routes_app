# routes_app/app/api.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import uuid
from .db import get_conn, reset_db as _reset_db

router = APIRouter()

# -------------------------
# Helpers
# -------------------------
def _ensure_schema():
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS routes (
                    id UUID PRIMARY KEY,
                    flight_id TEXT NOT NULL,
                    source_airport_code TEXT NOT NULL,
                    source_country TEXT NOT NULL,
                    destiny_airport_code TEXT NOT NULL,
                    destiny_country TEXT NOT NULL,
                    bag_cost INTEGER NOT NULL,
                    planned_start_date TIMESTAMP NOT NULL,
                    planned_end_date TIMESTAMP NOT NULL,
                    created_at TIMESTAMP NOT NULL DEFAULT NOW()
                );
            """)
        conn.commit()

_ensure_schema()

# -------------------------
# Schemas
# -------------------------
class RouteCreate(BaseModel):
    flightId: str = Field(min_length=1)
    sourceAirportCode: str = Field(min_length=1)
    sourceCountry: str = Field(min_length=1)
    destinyAirportCode: str = Field(min_length=1)
    destinyCountry: str = Field(min_length=1)
    bagCost: int = Field(ge=0)
    plannedStartDate: datetime
    plannedEndDate: datetime

class RouteUpdate(BaseModel):
    flightId: Optional[str] = None
    sourceAirportCode: Optional[str] = None
    sourceCountry: Optional[str] = None
    destinyAirportCode: Optional[str] = None
    destinyCountry: Optional[str] = None
    bagCost: Optional[int] = None
    plannedStartDate: Optional[datetime] = None
    plannedEndDate: Optional[datetime] = None

# -------------------------
# Endpoints
# -------------------------
@router.get("/routes/ping")
def routes_ping():
    return {"status": "ok"}

@router.post("/reset")
@router.post("/routes/reset")
def reset():
    _reset_db()
    return {"status": "ok", "message": "Todos los datos fueron eliminados"}

@router.get("/routes/count")
def count_routes():
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM routes")
            (count,) = cur.fetchone()
    return {"count": count}

@router.post("/routes", status_code=201)
def create_route(payload: RouteCreate):
    route_id = str(uuid.uuid4())
    
    # Validate dates
    if payload.departure_date >= payload.arrival_date:
        raise HTTPException(
            status_code=400, 
            detail="La fecha de salida debe ser anterior a la fecha de llegada"
        )
    
    with get_conn() as conn:
        with conn.cursor() as cur:
            try:
                cur.execute(
                    """
                    INSERT INTO routes (id, origin, destination, departure_date, arrival_date, capacity, description)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    RETURNING created_at
                    """,
                    (
                        route_id,
                        payload.origin,
                        payload.destination,
                        payload.departure_date,
                        payload.arrival_date,
                        payload.capacity,
                        payload.description or '',
                    ),
                )
                (created_at,) = cur.fetchone()
                return {"id": route_id, "createdAt": created_at.isoformat()}
            except Exception as e:
                raise HTTPException(status_code=400, detail=str(e))

@router.get("/routes/{route_id}")
def get_route(route_id: str):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, origin, destination, departure_date, arrival_date, 
                       capacity, description, created_at
                FROM routes WHERE id = %s
                """,
                (route_id,)
            )
            row = cur.fetchone()
            if not row:
                raise HTTPException(status_code=404, detail="Ruta no encontrada")
            
            (id, origin, destination, departure_date, arrival_date, 
             capacity, description, created_at) = row
            
            return {
                "id": str(id),
                "origin": origin,
                "destination": destination,
                "departureDate": departure_date.isoformat(),
                "arrivalDate": arrival_date.isoformat(),
                "capacity": capacity,
                "description": description or "",
                "createdAt": created_at.isoformat(),
            }

@router.get("/routes")
def list_routes(skip: int = 0, limit: int = 100):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, origin, destination, departure_date, arrival_date, 
                       capacity, description, created_at
                FROM routes 
                ORDER BY created_at DESC
                LIMIT %s OFFSET %s
                """,
                (limit, skip)
            )
            routes = []
            for row in cur.fetchall():
                (id, origin, destination, departure_date, arrival_date, 
                 capacity, description, created_at) = row
                routes.append({
                    "id": str(id),
                    "origin": origin,
                    "destination": destination,
                    "departureDate": departure_date.isoformat(),
                    "arrivalDate": arrival_date.isoformat(),
                    "capacity": capacity,
                    "description": description or "",
                    "createdAt": created_at.isoformat(),
                })
            return {"routes": routes, "total": len(routes)}

@router.patch("/routes/{route_id}")
def update_route(route_id: str, payload: RouteUpdate):
    with get_conn() as conn:
        with conn.cursor() as cur:
            # Verify route exists
            cur.execute("SELECT id FROM routes WHERE id = %s", (route_id,))
            if not cur.fetchone():
                raise HTTPException(status_code=404, detail="Ruta no encontrada")
            
            # Build update query dynamically
            updates = []
            values = []
            if payload.origin is not None:
                updates.append("origin = %s")
                values.append(payload.origin)
            if payload.destination is not None:
                updates.append("destination = %s")
                values.append(payload.destination)
            if payload.departure_date is not None:
                updates.append("departure_date = %s")
                values.append(payload.departure_date)
            if payload.arrival_date is not None:
                updates.append("arrival_date = %s")
                values.append(payload.arrival_date)
            if payload.capacity is not None:
                updates.append("capacity = %s")
                values.append(payload.capacity)
            if payload.description is not None:
                updates.append("description = %s")
                values.append(payload.description)
            
            if not updates:
                raise HTTPException(status_code=400, detail="No hay campos para actualizar")
            
            values.append(route_id)
            query = f"UPDATE routes SET {', '.join(updates)} WHERE id = %s"
            
            cur.execute(query, values)
            
            return {
                "status": "ruta actualizada",
                "msg": "la ruta ha sido actualizada",
                "message": "ruta actualizada",
            }

@router.delete("/routes/{route_id}")
def delete_route(route_id: str):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM routes WHERE id = %s", (route_id,))
            if cur.rowcount == 0:
                raise HTTPException(status_code=404, detail="Ruta no encontrada")
            
            return {"status": "ok", "message": "Ruta eliminada"}
