import pytest
from fastapi.testclient import TestClient
from app.main import app
import uuid
from datetime import datetime, timedelta

client = TestClient(app)

# Test data
VALID_ROUTE = {
    "origin": "Bogotá",
    "destination": "Medellín",
    "departure_date": (datetime.utcnow() + timedelta(days=1)).isoformat(),
    "arrival_date": (datetime.utcnow() + timedelta(days=1, hours=8)).isoformat(),
    "capacity": 4,
    "description": "Viaje cómodo y seguro"
}

INVALID_ROUTE = {
    "origin": "",  # empty
    "destination": "Medellín",
    "departure_date": (datetime.utcnow() + timedelta(days=1, hours=8)).isoformat(),
    "arrival_date": (datetime.utcnow() + timedelta(days=1)).isoformat(),  # before departure
    "capacity": 0,  # invalid
}

@pytest.fixture(autouse=True)
def reset_db():
    """Reset database before each test"""
    client.post("/reset")

def test_ping():
    """Test ping endpoint"""
    r = client.get("/ping")
    assert r.status_code == 200
    assert r.json()["status"] == "pong"

def test_routes_ping():
    """Test routes ping endpoint"""
    r = client.get("/routes/ping")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"

def test_reset():
    """Test reset endpoint"""
    r = client.post("/reset")
    assert r.status_code == 200
    assert "status" in r.json()

def test_reset_routes_endpoint():
    """Test reset routes endpoint"""
    r = client.post("/routes/reset")
    assert r.status_code == 200
    assert "status" in r.json()

def test_get_route_count():
    """Test route count endpoint"""
    # Initially should be 0
    r = client.get("/routes/count")
    assert r.status_code == 200
    assert r.json()["count"] == 0
    
    # Create route and check count
    client.post("/routes", json=VALID_ROUTE)
    r = client.get("/routes/count")
    assert r.status_code == 200
    assert r.json()["count"] == 1

def test_create_route_success():
    """Test successful route creation"""
    r = client.post("/routes", json=VALID_ROUTE)
    assert r.status_code == 201
    data = r.json()
    assert "id" in data
    assert "createdAt" in data
    # Verify UUID format
    uuid.UUID(data["id"])

def test_create_route_validation_error():
    """Test route creation with validation errors"""
    r = client.post("/routes", json=INVALID_ROUTE)
    assert r.status_code == 400

def test_create_route_invalid_dates():
    """Test route creation with invalid date order"""
    invalid_route = VALID_ROUTE.copy()
    invalid_route["departure_date"] = (datetime.utcnow() + timedelta(days=2)).isoformat()
    invalid_route["arrival_date"] = (datetime.utcnow() + timedelta(days=1)).isoformat()
    
    r = client.post("/routes", json=invalid_route)
    assert r.status_code == 400
    assert "fecha de salida debe ser anterior" in r.json()["detail"]

def test_create_route_missing_fields():
    """Test route creation with missing required fields"""
    incomplete_route = {"origin": "Bogotá"}
    r = client.post("/routes", json=incomplete_route)
    assert r.status_code == 400

def test_get_route_success():
    """Test successful route retrieval"""
    # Create route first
    create_resp = client.post("/routes", json=VALID_ROUTE)
    route_id = create_resp.json()["id"]
    
    # Get route
    r = client.get(f"/routes/{route_id}")
    assert r.status_code == 200
    data = r.json()
    assert data["id"] == route_id
    assert data["origin"] == VALID_ROUTE["origin"]
    assert data["destination"] == VALID_ROUTE["destination"]
    assert "departureDate" in data
    assert "arrivalDate" in data

def test_get_route_not_found():
    """Test get non-existent route"""
    fake_id = str(uuid.uuid4())
    r = client.get(f"/routes/{fake_id}")
    assert r.status_code == 404
    assert "Ruta no encontrada" in r.json()["detail"]

def test_list_routes_empty():
    """Test list routes when empty"""
    r = client.get("/routes")
    assert r.status_code == 200
    data = r.json()
    assert data["routes"] == []
    assert data["total"] == 0

def test_list_routes_with_data():
    """Test list routes with data"""
    # Create multiple routes
    client.post("/routes", json=VALID_ROUTE)
    
    route2 = VALID_ROUTE.copy()
    route2["destination"] = "Cali"
    client.post("/routes", json=route2)
    
    # List routes
    r = client.get("/routes")
    assert r.status_code == 200
    data = r.json()
    assert len(data["routes"]) == 2
    assert data["total"] == 2

def test_list_routes_pagination():
    """Test route pagination"""
    # Create multiple routes
    for i in range(5):
        route = VALID_ROUTE.copy()
        route["destination"] = f"Ciudad {i}"
        client.post("/routes", json=route)
    
    # Test pagination
    r = client.get("/routes?skip=2&limit=2")
    assert r.status_code == 200
    data = r.json()
    assert len(data["routes"]) == 2

def test_update_route_success():
    """Test successful route update"""
    # Create route first
    create_resp = client.post("/routes", json=VALID_ROUTE)
    route_id = create_resp.json()["id"]
    
    # Update route
    update_data = {
        "origin": "Cali",
        "capacity": 6
    }
    r = client.patch(f"/routes/{route_id}", json=update_data)
    assert r.status_code == 200
    data = r.json()
    assert "msg" in data
    assert "la ruta ha sido actualizada" in data["msg"]

def test_update_route_not_found():
    """Test update non-existent route"""
    fake_id = str(uuid.uuid4())
    update_data = {"origin": "Nueva Ciudad"}
    r = client.patch(f"/routes/{fake_id}", json=update_data)
    assert r.status_code == 404
    assert "Ruta no encontrada" in r.json()["detail"]

def test_update_route_no_fields():
    """Test update route with no fields"""
    # Create route first
    create_resp = client.post("/routes", json=VALID_ROUTE)
    route_id = create_resp.json()["id"]
    
    # Try to update with empty data
    r = client.patch(f"/routes/{route_id}", json={})
    assert r.status_code == 400
    assert "No hay campos para actualizar" in r.json()["detail"]

def test_delete_route_success():
    """Test successful route deletion"""
    # Create route first
    create_resp = client.post("/routes", json=VALID_ROUTE)
    route_id = create_resp.json()["id"]
    
    # Delete route
    r = client.delete(f"/routes/{route_id}")
    assert r.status_code == 200
    assert "Ruta eliminada" in r.json()["message"]
    
    # Verify it's deleted
    r = client.get(f"/routes/{route_id}")
    assert r.status_code == 404

def test_delete_route_not_found():
    """Test delete non-existent route"""
    fake_id = str(uuid.uuid4())
    r = client.delete(f"/routes/{fake_id}")
    assert r.status_code == 404
    assert "Ruta no encontrada" in r.json()["detail"]

def test_route_crud_integration():
    """Test complete CRUD cycle"""
    # Create
    create_resp = client.post("/routes", json=VALID_ROUTE)
    assert create_resp.status_code == 201
    route_id = create_resp.json()["id"]
    
    # Read
    get_resp = client.get(f"/routes/{route_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["origin"] == VALID_ROUTE["origin"]
    
    # Update
    update_data = {"origin": "Updated Origin"}
    update_resp = client.patch(f"/routes/{route_id}", json=update_data)
    assert update_resp.status_code == 200
    
    # Verify update
    get_resp = client.get(f"/routes/{route_id}")
    assert get_resp.json()["origin"] == "Updated Origin"
    
    # Delete
    delete_resp = client.delete(f"/routes/{route_id}")
    assert delete_resp.status_code == 200
    
    # Verify deletion
    get_resp = client.get(f"/routes/{route_id}")
    assert get_resp.status_code == 404
