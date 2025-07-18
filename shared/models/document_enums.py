from enum import Enum

class DocumentType(str, Enum):
    STANDUP = "standup"
    CRITICAL_ISSUE = "critical_issue"
    SERVICE_STATUS = "service_status"
    UPDATE = "update"

class ServiceStatus(str, Enum):
    UP = "up"
    DOWN = "down"
    STARTING = "starting"