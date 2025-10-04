from fastapi import APIRouter
from datetime import datetime
from app.services.supabase_service import supabase_service
from app.models.schemas import HealthResponse
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint to verify the API and Supabase connectivity."""
    database_connected = False
    storage_connected = False

    if supabase_service.client is None:
        logger.warning("Supabase client not configured")
    else:
        try:
            # Test database connectivity
            result = supabase_service.client.table('documents').select('id').limit(1).execute()
            database_connected = True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")

        try:
            # Test storage connectivity
            buckets = supabase_service.client.storage.list_buckets()
            storage_connected = True
        except Exception as e:
            logger.error(f"Storage health check failed: {e}")

    overall_status = "healthy" if database_connected and storage_connected else "unhealthy"

    return HealthResponse(
        status=overall_status,
        timestamp=datetime.utcnow(),
        version="1.0.0",
        database_connected=database_connected,
        storage_connected=storage_connected,
    )