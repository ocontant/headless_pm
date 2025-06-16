import pytest
from datetime import datetime, timedelta
from sqlmodel import Session, select
from src.models.models import Service, Agent
from src.models.document_enums import ServiceStatus

def test_service_registration(session: Session, sample_data):
    """Test registering a new service"""
    backend_dev = sample_data["agents"]["backend_dev"]
    
    service = Service(
        service_name="api",
        owner_agent_id=backend_dev.agent_id,
        port=8000,
        status=ServiceStatus.UP,
        meta_data={"start_command": "uvicorn main:app", "version": "1.0.0"}
    )
    session.add(service)
    session.commit()
    
    saved_service = session.get(Service, service.id)
    assert saved_service.service_name == "api"
    assert saved_service.port == 8000
    assert saved_service.status == ServiceStatus.UP
    assert saved_service.meta_data["version"] == "1.0.0"

def test_service_unique_name(session: Session, sample_data):
    """Test that service names must be unique"""
    frontend_dev = sample_data["agents"]["frontend_dev"]
    backend_dev = sample_data["agents"]["backend_dev"]
    
    # Create first service
    service1 = Service(
        service_name="web",
        owner_agent_id=frontend_dev.agent_id,
        port=3000,
        status=ServiceStatus.UP
    )
    session.add(service1)
    session.commit()
    
    # Try to create duplicate service name
    service2 = Service(
        service_name="web",
        owner_agent_id=backend_dev.agent_id,
        port=3001,
        status=ServiceStatus.UP
    )
    session.add(service2)
    
    with pytest.raises(Exception):  # Should raise integrity error
        session.commit()

def test_service_heartbeat(session: Session, sample_data):
    """Test service heartbeat updates"""
    qa = sample_data["agents"]["qa"]
    
    # Create service
    service = Service(
        service_name="test-runner",
        owner_agent_id=qa.agent_id,
        port=4000,
        status=ServiceStatus.UP,
        last_heartbeat=datetime.utcnow()
    )
    session.add(service)
    session.commit()
    
    original_heartbeat = service.last_heartbeat
    
    # Update heartbeat
    service.last_heartbeat = datetime.utcnow()
    service.updated_at = datetime.utcnow()
    session.add(service)
    session.commit()
    
    updated_service = session.get(Service, service.id)
    assert updated_service.last_heartbeat > original_heartbeat

def test_service_status_transitions(session: Session, sample_data):
    """Test service status changes"""
    backend_dev = sample_data["agents"]["backend_dev"]
    
    # Create service in DOWN state
    service = Service(
        service_name="database",
        owner_agent_id=backend_dev.agent_id,
        port=5432,
        status=ServiceStatus.DOWN
    )
    session.add(service)
    session.commit()
    
    # Update to STARTING
    service.status = ServiceStatus.STARTING
    service.updated_at = datetime.utcnow()
    session.add(service)
    session.commit()
    
    assert session.get(Service, service.id).status == ServiceStatus.STARTING
    
    # Update to UP
    service.status = ServiceStatus.UP
    service.last_heartbeat = datetime.utcnow()
    service.updated_at = datetime.utcnow()
    session.add(service)
    session.commit()
    
    assert session.get(Service, service.id).status == ServiceStatus.UP

def test_service_without_port(session: Session, sample_data):
    """Test service that doesn't need a port"""
    architect = sample_data["agents"]["architect"]
    
    # Create a background worker service without port
    service = Service(
        service_name="task-scheduler",
        owner_agent_id=architect.agent_id,
        status=ServiceStatus.UP,
        meta_data={"type": "background_worker", "interval": "5m"}
    )
    session.add(service)
    session.commit()
    
    saved_service = session.get(Service, service.id)
    assert saved_service.port is None
    assert saved_service.meta_data["type"] == "background_worker"

def test_multiple_services_per_agent(session: Session, sample_data):
    """Test that an agent can own multiple services"""
    backend_dev = sample_data["agents"]["backend_dev"]
    
    services = [
        Service(
            service_name="api-v1",
            owner_agent_id=backend_dev.agent_id,
            port=8000,
            status=ServiceStatus.UP
        ),
        Service(
            service_name="api-v2",
            owner_agent_id=backend_dev.agent_id,
            port=8001,
            status=ServiceStatus.UP
        ),
        Service(
            service_name="worker",
            owner_agent_id=backend_dev.agent_id,
            status=ServiceStatus.UP
        )
    ]
    
    for service in services:
        session.add(service)
    session.commit()
    
    # Query all services owned by backend_dev
    backend_services = session.exec(
        select(Service).where(Service.owner_agent_id == backend_dev.agent_id)
    ).all()
    
    assert len(backend_services) == 3
    assert {s.service_name for s in backend_services} == {"api-v1", "api-v2", "worker"}

def test_service_meta_data_update(session: Session, sample_data):
    """Test updating service meta_data"""
    frontend_dev = sample_data["agents"]["frontend_dev"]
    
    # Create service with initial meta_data
    service = Service(
        service_name="frontend",
        owner_agent_id=frontend_dev.agent_id,
        port=3000,
        status=ServiceStatus.UP,
        meta_data={"framework": "react", "version": "18.0"}
    )
    session.add(service)
    session.commit()
    
    # Update meta_data
    service.meta_data = {
        "framework": "react",
        "version": "18.2",
        "build": "production",
        "features": ["ssr", "hot-reload"]
    }
    service.updated_at = datetime.utcnow()
    session.add(service)
    session.commit()
    
    updated_service = session.get(Service, service.id)
    assert updated_service.meta_data["version"] == "18.2"
    assert "build" in updated_service.meta_data
    assert "hot-reload" in updated_service.meta_data["features"]