from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select
from typing import List
from datetime import datetime

from src.models.database import get_session
from src.models.models import Service
from src.models.document_enums import ServiceStatus
from src.api.schemas import ServiceRegisterRequest, ServiceResponse
from src.api.dependencies import verify_api_key

router = APIRouter(prefix="/api/v1/services", tags=["Services"], dependencies=[Depends(verify_api_key)])

@router.post("/register", response_model=ServiceResponse,
    summary="Register or update service",
    description="Register a new service or update existing service status")
def register_service(
    request: ServiceRegisterRequest,
    agent_id: str = Query(..., description="Agent ID of the service owner"),
    db: Session = Depends(get_session)
):
    # Check if service already exists
    service = db.exec(
        select(Service).where(Service.service_name == request.service_name)
    ).first()
    
    if service:
        # Update existing service
        service.owner_agent_id = agent_id
        service.port = request.port
        service.status = request.status
        service.meta_data = request.meta_data
        service.last_heartbeat = datetime.utcnow()
        service.updated_at = datetime.utcnow()
    else:
        # Create new service
        service = Service(
            service_name=request.service_name,
            owner_agent_id=agent_id,
            port=request.port,
            status=request.status,
            meta_data=request.meta_data,
            last_heartbeat=datetime.utcnow()
        )
        db.add(service)
    
    db.commit()
    db.refresh(service)
    
    return service

@router.get("", response_model=List[ServiceResponse],
    summary="List all services",
    description="Get list of all registered services")
def list_services(db: Session = Depends(get_session)):
    services = db.exec(select(Service).order_by(Service.service_name)).all()
    return services

@router.post("/{service_name}/heartbeat", response_model=ServiceResponse,
    summary="Send heartbeat",
    description="Update service heartbeat to keep it alive")
def service_heartbeat(
    service_name: str,
    agent_id: str = Query(..., description="Agent ID sending the heartbeat"),
    db: Session = Depends(get_session)
):
    service = db.exec(
        select(Service).where(Service.service_name == service_name)
    ).first()
    
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    
    # Verify ownership
    if service.owner_agent_id != agent_id:
        raise HTTPException(status_code=403, detail="Only service owner can send heartbeat")
    
    # Update heartbeat
    service.last_heartbeat = datetime.utcnow()
    service.updated_at = datetime.utcnow()
    
    # Ensure status is UP if sending heartbeat
    if service.status != ServiceStatus.UP:
        service.status = ServiceStatus.UP
    
    db.add(service)
    db.commit()
    db.refresh(service)
    
    return service

@router.delete("/{service_name}",
    summary="Unregister service",
    description="Remove a service from the registry")
def unregister_service(
    service_name: str,
    agent_id: str = Query(..., description="Agent ID requesting deletion"),
    db: Session = Depends(get_session)
):
    service = db.exec(
        select(Service).where(Service.service_name == service_name)
    ).first()
    
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    
    # Verify ownership
    if service.owner_agent_id != agent_id:
        raise HTTPException(status_code=403, detail="Only service owner can unregister service")
    
    db.delete(service)
    db.commit()
    
    return {"message": f"Service {service_name} unregistered successfully"}