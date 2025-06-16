"""
Service Health Checker - Periodically pings registered services
"""

import asyncio
import httpx
from datetime import datetime, timedelta
from typing import Optional
from sqlmodel import Session, select
import logging

from src.models.database import get_session
from src.models.models import Service
from src.models.document_enums import ServiceStatus

logger = logging.getLogger(__name__)

class ServiceHealthChecker:
    def __init__(self, check_interval: int = 30):
        """
        Initialize the health checker
        
        Args:
            check_interval: Seconds between health checks (default: 30)
        """
        self.check_interval = check_interval
        self.running = False
        self._task: Optional[asyncio.Task] = None
        
    async def start(self):
        """Start the health checker background task"""
        if self.running:
            logger.warning("Health checker already running")
            return
            
        self.running = True
        self._task = asyncio.create_task(self._health_check_loop())
        logger.info(f"Health checker started with {self.check_interval}s interval")
        
    async def stop(self):
        """Stop the health checker"""
        self.running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("Health checker stopped")
        
    async def _health_check_loop(self):
        """Main health check loop"""
        while self.running:
            try:
                await self._check_all_services()
                await asyncio.sleep(self.check_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in health check loop: {e}")
                await asyncio.sleep(self.check_interval)
                
    async def _check_all_services(self):
        """Check health of all registered services"""
        db = next(get_session())
        try:
            services = db.exec(select(Service)).all()
            
            # Create tasks for all service checks
            tasks = []
            for service in services:
                task = asyncio.create_task(self._check_service(service, db))
                tasks.append(task)
                
            # Wait for all checks to complete
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)
                
            db.commit()
        except Exception as e:
            logger.error(f"Error checking services: {e}")
            db.rollback()
        finally:
            db.close()
            
    async def _check_service(self, service: Service, db: Session):
        """Check health of a single service"""
        try:
            # Skip if service hasn't been registered long enough
            if not service.ping_url:
                logger.warning(f"Service {service.service_name} has no ping URL")
                return
                
            # Perform health check
            async with httpx.AsyncClient(timeout=10.0) as client:
                try:
                    response = await client.get(service.ping_url)
                    is_healthy = response.status_code == 200
                    
                    # Update service status
                    service.last_ping_at = datetime.utcnow()
                    service.last_ping_success = is_healthy
                    
                    if is_healthy:
                        if service.status != ServiceStatus.UP:
                            logger.info(f"Service {service.service_name} is now UP")
                        service.status = ServiceStatus.UP
                    else:
                        if service.status == ServiceStatus.UP:
                            logger.warning(f"Service {service.service_name} returned {response.status_code}")
                        service.status = ServiceStatus.DOWN
                        
                except httpx.RequestError as e:
                    # Connection failed
                    logger.error(f"Failed to connect to {service.service_name}: {e}")
                    service.last_ping_at = datetime.utcnow()
                    service.last_ping_success = False
                    service.status = ServiceStatus.DOWN
                    
            service.updated_at = datetime.utcnow()
            db.add(service)
            
        except Exception as e:
            logger.error(f"Error checking service {service.service_name}: {e}")
            
    async def check_service_now(self, service_name: str) -> bool:
        """
        Check a specific service immediately
        
        Returns:
            bool: True if service is healthy
        """
        db = next(get_session())
        try:
            service = db.exec(
                select(Service).where(Service.service_name == service_name)
            ).first()
            
            if not service:
                logger.error(f"Service {service_name} not found")
                return False
                
            await self._check_service(service, db)
            db.commit()
            
            return service.last_ping_success or False
            
        except Exception as e:
            logger.error(f"Error checking service {service_name}: {e}")
            db.rollback()
            return False
        finally:
            db.close()

# Global instance
health_checker = ServiceHealthChecker()