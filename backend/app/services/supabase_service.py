"""
Supabase service for database and storage operations.
"""
import os
from typing import Optional, Dict, Any, List
from supabase import Client, create_client
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class SupabaseService:
    """Service class for Supabase operations."""

    def __init__(self):
        """Initialize Supabase client."""
        # Check if we have valid Supabase credentials
        if not settings.SUPABASE_URL or not settings.SUPABASE_KEY or \
           settings.SUPABASE_URL.startswith('your_') or settings.SUPABASE_KEY.startswith('your_'):
            logger.warning("Supabase credentials not configured. Supabase operations will be disabled.")
            self.client = None
        else:
            try:
                self.client: Client = create_client(
                    supabase_url=settings.SUPABASE_URL,
                    supabase_key=settings.SUPABASE_KEY
                )
            except Exception as e:
                logger.error(f"Failed to initialize Supabase client: {e}")
                self.client = None

    def _check_client(self):
        """Check if Supabase client is available."""
        if self.client is None:
            raise Exception("Supabase client not configured. Please set valid SUPABASE_URL and SUPABASE_KEY environment variables.")
    
    async def create_document_record(
        self,
        filename: str,
        processing_options: Dict[str, Any]
    ) -> str:
        """Create a new document record in the database."""
        self._check_client()
        try:
            result = self.client.table('documents').insert({
                'filename': filename,
                'status': 'queued',
                'processing_options': processing_options
            }).execute()

            if result.data:
                return result.data[0]['id']
            else:
                raise Exception("Failed to create document record")

        except Exception as e:
            logger.error(f"Error creating document record: {e}")
            raise
    
    async def get_document(self, document_id: str) -> Optional[Dict[str, Any]]:
        """Get document by ID."""
        try:
            result = self.client.table('documents').select('*').eq('id', document_id).execute()
            
            if result.data:
                return result.data[0]
            return None
            
        except Exception as e:
            logger.error(f"Error getting document {document_id}: {e}")
            raise
    
    async def update_document_status(
        self, 
        document_id: str, 
        status: str,
        error_message: Optional[str] = None
    ) -> bool:
        """Update document status."""
        try:
            update_data = {'status': status}
            
            if status == 'complete':
                update_data['completed_at'] = 'now()'
            
            if error_message:
                update_data['error_message'] = error_message
            
            result = self.client.table('documents').update(update_data).eq('id', document_id).execute()
            
            return len(result.data) > 0
            
        except Exception as e:
            logger.error(f"Error updating document status {document_id}: {e}")
            raise
    
    async def upload_file(
        self, 
        bucket: str, 
        file_path: str, 
        file_content: bytes,
        content_type: str
    ) -> bool:
        """Upload file to Supabase storage."""
        try:
            result = self.client.storage.from_(bucket).upload(
                path=file_path,
                file=file_content,
                file_options={'content-type': content_type}
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Error uploading file to {bucket}/{file_path}: {e}")
            raise
    
    async def download_file(self, bucket: str, file_path: str) -> bytes:
        """Download file from Supabase storage."""
        try:
            result = self.client.storage.from_(bucket).download(file_path)
            return result
            
        except Exception as e:
            logger.error(f"Error downloading file from {bucket}/{file_path}: {e}")
            raise
    
    async def get_file_url(self, bucket: str, file_path: str, expires_in: int = 3600) -> str:
        """Get signed URL for file access."""
        try:
            result = self.client.storage.from_(bucket).create_signed_url(
                path=file_path,
                expires_in=expires_in
            )
            
            # The supabase-py client returns a response object with 'signedURL' (note the case)
            # Handle different response formats
            if isinstance(result, dict):
                # Direct dictionary response
                url = result.get('signedURL') or result.get('signedUrl') or result.get('signed_url')
                if url:
                    return url
            elif hasattr(result, 'get'):
                # Object with get method
                url = result.get('signedURL') or result.get('signedUrl') or result.get('signed_url')
                if url:
                    return url
                    
            raise Exception(f"Could not extract signed URL from response: {result}")
                
        except Exception as e:
            logger.error(f"Error creating signed URL for {bucket}/{file_path}: {e}")
            raise
    
    async def delete_file(self, bucket: str, file_path: str) -> bool:
        """Delete file from Supabase storage."""
        try:
            result = self.client.storage.from_(bucket).remove([file_path])
            return True
            
        except Exception as e:
            logger.error(f"Error deleting file from {bucket}/{file_path}: {e}")
            raise


# Global instance
supabase_service = SupabaseService()