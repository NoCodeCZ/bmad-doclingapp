"""
Integration tests for Supabase service.
"""
import pytest
import asyncio
from unittest.mock import patch, MagicMock
from app.services.supabase_service import supabase_service
from app.core.config import settings


class TestSupabaseIntegration:
    """Test Supabase service integration."""
    
    @pytest.fixture
    def mock_supabase_client(self):
        """Mock Supabase client for testing."""
        with patch('app.services.supabase_service.create_client') as mock_create:
            mock_client = MagicMock()
            mock_create.return_value = mock_client
            yield mock_client
    
    @pytest.mark.asyncio
    async def test_create_document_record(self, mock_supabase_client):
        """Test creating a document record."""
        # Mock the database response
        mock_supabase_client.table.return_value.insert.return_value.execute.return_value.data = [
            {'id': 'test-id', 'filename': 'test.pdf', 'status': 'queued'}
        ]
        
        # Test creating a document record
        processing_options = {'ocr_enabled': False, 'processing_mode': 'fast'}
        document_id = await supabase_service.create_document_record(
            'test.pdf', 
            processing_options
        )
        
        assert document_id == 'test-id'
        mock_supabase_client.table.assert_called_with('documents')
    
    @pytest.mark.asyncio
    async def test_get_document(self, mock_supabase_client):
        """Test retrieving a document."""
        # Mock the database response
        mock_document = {
            'id': 'test-id',
            'filename': 'test.pdf',
            'status': 'complete',
            'created_at': '2025-10-04T07:00:00Z'
        }
        mock_supabase_client.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [
            mock_document
        ]
        
        # Test getting a document
        document = await supabase_service.get_document('test-id')
        
        assert document == mock_document
        mock_supabase_client.table.assert_called_with('documents')
    
    @pytest.mark.asyncio
    async def test_update_document_status(self, mock_supabase_client):
        """Test updating document status."""
        # Mock the database response
        mock_supabase_client.table.return_value.update.return_value.eq.return_value.execute.return_value.data = [
            {'id': 'test-id', 'status': 'complete'}
        ]
        
        # Test updating status
        success = await supabase_service.update_document_status(
            'test-id', 
            'complete'
        )
        
        assert success is True
        mock_supabase_client.table.assert_called_with('documents')
    
    @pytest.mark.asyncio
    async def test_upload_file(self, mock_supabase_client):
        """Test uploading a file to storage."""
        # Mock the storage response
        mock_supabase_client.storage.from_.return_value.upload.return_value = True
        
        # Test file upload
        success = await supabase_service.upload_file(
            'uploads',
            'test-id/test.pdf',
            b'file content',
            'application/pdf'
        )
        
        assert success is True
        mock_supabase_client.storage.from_.assert_called_with('uploads')
    
    @pytest.mark.asyncio
    async def test_download_file(self, mock_supabase_client):
        """Test downloading a file from storage."""
        # Mock the storage response
        expected_content = b'file content'
        mock_supabase_client.storage.from_.return_value.download.return_value = expected_content
        
        # Test file download
        content = await supabase_service.download_file('uploads', 'test-id/test.pdf')
        
        assert content == expected_content
        mock_supabase_client.storage.from_.assert_called_with('uploads')
    
    @pytest.mark.asyncio
    async def test_get_file_url(self, mock_supabase_client):
        """Test creating a signed URL for file access."""
        # Mock the storage response
        mock_url = 'https://signed-url.example.com'
        mock_supabase_client.storage.from_.return_value.create_signed_url.return_value.data = {
            'signedUrl': mock_url
        }
        
        # Test creating signed URL
        url = await supabase_service.get_file_url('uploads', 'test-id/test.pdf')
        
        assert url == mock_url
        mock_supabase_client.storage.from_.assert_called_with('uploads')
    
    @pytest.mark.asyncio
    async def test_delete_file(self, mock_supabase_client):
        """Test deleting a file from storage."""
        # Mock the storage response
        mock_supabase_client.storage.from_.return_value.remove.return_value = True
        
        # Test file deletion
        success = await supabase_service.delete_file('uploads', 'test-id/test.pdf')
        
        assert success is True
        mock_supabase_client.storage.from_.assert_called_with('uploads')


# Manual integration tests (run with real Supabase credentials)
@pytest.mark.integration
class TestSupabaseRealIntegration:
    """Real integration tests with Supabase (requires valid credentials)."""
    
    @pytest.mark.asyncio
    async def test_real_connection(self):
        """Test real Supabase connection (only runs with valid credentials)."""
        if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
            pytest.skip("Supabase credentials not configured")
        
        try:
            # Test basic connectivity by attempting to create a test document
            processing_options = {'ocr_enabled': False, 'processing_mode': 'fast'}
            document_id = await supabase_service.create_document_record(
                'integration-test.pdf', 
                processing_options
            )
            
            # Verify the document was created
            document = await supabase_service.get_document(document_id)
            assert document is not None
            assert document['filename'] == 'integration-test.pdf'
            assert document['status'] == 'queued'
            
            # Clean up - update status to failed to mark as test
            await supabase_service.update_document_status(
                document_id, 
                'failed', 
                'Integration test cleanup'
            )
            
        except Exception as e:
            pytest.fail(f"Real Supabase integration test failed: {e}")


if __name__ == "__main__":
    # Run manual integration test
    print("Running Supabase integration tests...")
    
    async def run_integration_test():
        try:
            await TestSupabaseRealIntegration().test_real_connection()
            print("✅ Supabase integration test passed!")
        except Exception as e:
            print(f"❌ Supabase integration test failed: {e}")
    
    asyncio.run(run_integration_test())