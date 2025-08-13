from fastapi import APIRouter, Response
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    REGISTRY,
    CollectorRegistry,
    generate_latest,
)

router = APIRouter()


@router.get("/")
async def get_metrics_endpoint():
    """
    Get all Prometheus metrics.
    Combines both Instrumentator metrics and custom business metrics.
    """
    # Generate metrics from default registry (includes both custom and Instrumentator metrics)
    metrics_output = generate_latest(REGISTRY)
    return Response(content=metrics_output, media_type=CONTENT_TYPE_LATEST)
