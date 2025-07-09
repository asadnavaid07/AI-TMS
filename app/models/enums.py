from enum import Enum

class CategoryEnum(str, Enum):
    IT_SUPPORT = "IT Support"
    HR = "Human Resources"
    FACILITIES = "Facilities"
    FINANCE = "Finance"
    ADMINISTRATION = "Administration"
    PROCUREMENT = "Procurement"
    SECURITY = "Security"
    OPERATIONS = "Operations"
    COMPLIANCE = "Compliance"
    GENERAL = "General Inquiry"
    ACCESS_CONTROL = "Access Control"
    ADMIN="Admin"
    NETWORK="Network"

class SeverityEnum(str,Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


class StatusEnum(str,Enum):
    NEW = "New"
    IN_PROGRESS = "In Progress"
    RESOLVED = "Resolved"
    CLOSED = "Closed"

