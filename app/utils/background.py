import json
from datetime import datetime
from app.models import IncidentAnalysis,IncidentRequest
from app.utils.logging import logger

async def log_incident_metrics(incident:IncidentRequest,analysis:IncidentAnalysis):
    metrics={
        "timestamp": analysis.timestamp.isoformat(),
        "category": analysis.classification.category,
        "severity": analysis.classification.severity,
        "confidence": analysis.classification.confidence_score,
        "processing_time_ms": analysis.processing_time_ms,
        "department": incident.department
    }

    logger.info(f"Incident metrics: {json.dumps(metrics)}")
