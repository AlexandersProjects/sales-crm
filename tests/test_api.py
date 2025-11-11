"""
Tests for the Sales CRM API endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


def test_root_endpoint(client: TestClient) -> None:
    """Test the root endpoint returns correct information."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Sales CRM API"
    assert data["version"] == "0.1.0"
    assert data["docs"] == "/docs"


def test_health_check(client: TestClient) -> None:
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_create_tenant(client: TestClient) -> None:
    """Test creating a new tenant."""
    tenant_data = {"name": "Test Company"}
    response = client.post("/api/tenants", json=tenant_data)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Company"
    assert "id" in data
    assert "created_at" in data


def test_list_tenants(client: TestClient) -> None:
    """Test listing tenants."""
    # Create a tenant first
    client.post("/api/tenants", json={"name": "Company 1"})
    client.post("/api/tenants", json={"name": "Company 2"})

    response = client.get("/api/tenants")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


def test_get_tenant(client: TestClient) -> None:
    """Test getting a specific tenant."""
    # Create a tenant
    create_response = client.post("/api/tenants", json={"name": "Test Company"})
    tenant_id = create_response.json()["id"]

    # Get the tenant
    response = client.get(f"/api/tenants/{tenant_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == tenant_id
    assert data["name"] == "Test Company"


def test_get_nonexistent_tenant(client: TestClient) -> None:
    """Test getting a tenant that doesn't exist."""
    response = client.get("/api/tenants/999")
    assert response.status_code == 404


def test_create_lead(client: TestClient) -> None:
    """Test creating a new lead."""
    # Create a tenant first
    tenant_response = client.post("/api/tenants", json={"name": "Test Company"})
    tenant_id = tenant_response.json()["id"]

    # Create a lead
    lead_data = {
        "tenant_id": tenant_id,
        "name": "John Doe",
        "email": "john@example.com",
        "phone": "+1-555-0101",
        "company": "Acme Corp",
        "status": "new",
        "notes": "Interested in product"
    }
    response = client.post("/api/leads", json=lead_data)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "John Doe"
    assert data["email"] == "john@example.com"
    assert data["tenant_id"] == tenant_id


def test_create_lead_without_tenant(client: TestClient) -> None:
    """Test creating a lead with non-existent tenant fails."""
    lead_data = {
        "tenant_id": 999,
        "name": "John Doe",
        "email": "john@example.com"
    }
    response = client.post("/api/leads", json=lead_data)
    assert response.status_code == 404


def test_list_leads(client: TestClient) -> None:
    """Test listing leads."""
    # Create tenant and leads
    tenant_response = client.post("/api/tenants", json={"name": "Test Company"})
    tenant_id = tenant_response.json()["id"]

    client.post("/api/leads", json={
        "tenant_id": tenant_id,
        "name": "Lead 1",
        "email": "lead1@example.com"
    })
    client.post("/api/leads", json={
        "tenant_id": tenant_id,
        "name": "Lead 2",
        "email": "lead2@example.com"
    })

    response = client.get("/api/leads")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


def test_filter_leads_by_tenant(client: TestClient) -> None:
    """Test filtering leads by tenant ID."""
    # Create two tenants
    tenant1_response = client.post("/api/tenants", json={"name": "Company 1"})
    tenant1_id = tenant1_response.json()["id"]
    tenant2_response = client.post("/api/tenants", json={"name": "Company 2"})
    tenant2_id = tenant2_response.json()["id"]

    # Create leads for different tenants
    client.post("/api/leads", json={"tenant_id": tenant1_id, "name": "Lead 1"})
    client.post("/api/leads", json={"tenant_id": tenant2_id, "name": "Lead 2"})

    # Filter by tenant 1
    response = client.get(f"/api/leads?tenant_id={tenant1_id}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["tenant_id"] == tenant1_id


def test_update_lead(client: TestClient) -> None:
    """Test updating a lead."""
    # Create tenant and lead
    tenant_response = client.post("/api/tenants", json={"name": "Test Company"})
    tenant_id = tenant_response.json()["id"]
    lead_response = client.post("/api/leads", json={
        "tenant_id": tenant_id,
        "name": "John Doe",
        "status": "new"
    })
    lead_id = lead_response.json()["id"]

    # Update the lead
    update_data = {"status": "contacted", "notes": "Called customer"}
    response = client.put(f"/api/leads/{lead_id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "contacted"
    assert data["notes"] == "Called customer"


def test_delete_lead(client: TestClient) -> None:
    """Test deleting a lead."""
    # Create tenant and lead
    tenant_response = client.post("/api/tenants", json={"name": "Test Company"})
    tenant_id = tenant_response.json()["id"]
    lead_response = client.post("/api/leads", json={
        "tenant_id": tenant_id,
        "name": "John Doe"
    })
    lead_id = lead_response.json()["id"]

    # Delete the lead
    response = client.delete(f"/api/leads/{lead_id}")
    assert response.status_code == 204

    # Verify it's deleted
    get_response = client.get(f"/api/leads/{lead_id}")
    assert get_response.status_code == 404


def test_ai_email_generation_without_api_key(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test AI email generation fails gracefully without API key."""
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    request_data = {
        "lead_name": "John Doe",
        "company": "Acme Corp",
        "tone": "professional"
    }
    response = client.post("/api/ai/generate-email", json=request_data)
    assert response.status_code == 503

