from enum import Enum

class TaskStatus(str, Enum):
    CREATED = "created"
    EVALUATION = "evaluation"
    APPROVED = "approved"
    UNDER_WORK = "under_work"
    DEV_DONE = "dev_done"
    QA_DONE = "qa_done"
    DOCUMENTATION_DONE = "documentation_done"
    COMMITTED = "committed"

class AgentRole(str, Enum):
    FRONTEND_DEV = "frontend_dev"
    BACKEND_DEV = "backend_dev"
    QA = "qa"
    ARCHITECT = "architect"
    PM = "pm"

class DifficultyLevel(str, Enum):
    JUNIOR = "junior"
    SENIOR = "senior"
    PRINCIPAL = "principal"

class TaskComplexity(str, Enum):
    MINOR = "minor"  # Commit directly to main
    MAJOR = "major"  # Requires PR