"""
Tests for enhanced status endpoint with progress stages and time calculations.
"""
import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


class TestStatusEndpoint:
    """Test suite for /api/status/{document_id} endpoint."""

    @pytest.fixture
    def mock_document_queued(self):
        """Mock document in queued state."""
        created_time = datetime.now(timezone.utc) - timedelta(seconds=3)
        return {
            'id': 'test-doc-123',
            'filename': 'test.pdf',
            'status': 'queued',
            'processing_options': {
                'mode': 'fast',
                'ocr_enabled': False
            },
            'created_at': created_time.isoformat(),
            'completed_at': None,
            'error_message': None
        }

    @pytest.fixture
    def mock_document_processing(self):
        """Mock document in processing state."""
        created_time = datetime.now(timezone.utc) - timedelta(seconds=15)
        return {
            'id': 'test-doc-123',
            'filename': 'test.pdf',
            'status': 'processing',
            'processing_options': {
                'mode': 'fast',
                'ocr_enabled': False
            },
            'created_at': created_time.isoformat(),
            'completed_at': None,
            'error_message': None
        }

    @pytest.fixture
    def mock_document_complete(self):
        """Mock document in complete state."""
        created_time = datetime.now(timezone.utc) - timedelta(seconds=30)
        completed_time = datetime.now(timezone.utc)
        return {
            'id': 'test-doc-123',
            'filename': 'test.pdf',
            'status': 'complete',
            'processing_options': {
                'mode': 'fast',
                'ocr_enabled': False
            },
            'created_at': created_time.isoformat(),
            'completed_at': completed_time.isoformat(),
            'error_message': None
        }

    @pytest.fixture
    def mock_document_failed(self):
        """Mock document in failed state."""
        created_time = datetime.now(timezone.utc) - timedelta(seconds=10)
        return {
            'id': 'test-doc-123',
            'filename': 'test.pdf',
            'status': 'failed',
            'processing_options': {
                'mode': 'fast',
                'ocr_enabled': False
            },
            'created_at': created_time.isoformat(),
            'completed_at': None,
            'error_message': 'Processing failed: invalid file format'
        }

    @patch('app.api.endpoints.status.supabase_service.get_document')
    async def test_get_status_queued_uploading_stage(self, mock_get_doc, mock_document_queued):
        """Test status endpoint returns 'Uploading file...' for very recent queued documents."""
        # Set created time to less than 5 seconds ago
        created_time = datetime.now(timezone.utc) - timedelta(seconds=2)
        mock_document_queued['created_at'] = created_time.isoformat()
        mock_get_doc.return_value = mock_document_queued

        response = client.get('/api/status/test-doc-123')

        assert response.status_code == 200
        data = response.json()

        assert data['id'] == 'test-doc-123'
        assert data['status'] == 'queued'
        assert data['progress_stage'] == 'Uploading file...'
        assert data['elapsed_time'] >= 1
        assert data['elapsed_time'] <= 5
        assert data['progress'] >= 0
        assert data['progress'] <= 10

    @patch('app.api.endpoints.status.supabase_service.get_document')
    async def test_get_status_queued_waiting_stage(self, mock_get_doc, mock_document_queued):
        """Test status endpoint returns 'Queued for processing' for queued documents >= 5 seconds."""
        # Set created time to more than 5 seconds ago
        created_time = datetime.now(timezone.utc) - timedelta(seconds=8)
        mock_document_queued['created_at'] = created_time.isoformat()
        mock_get_doc.return_value = mock_document_queued

        response = client.get('/api/status/test-doc-123')

        assert response.status_code == 200
        data = response.json()

        assert data['status'] == 'queued'
        assert data['progress_stage'] == 'Queued for processing'
        assert data['elapsed_time'] >= 7

    @patch('app.api.endpoints.status.supabase_service.get_document')
    async def test_get_status_processing_converting_stage(self, mock_get_doc, mock_document_processing):
        """Test status endpoint returns 'Converting document' for processing < 100 seconds."""
        created_time = datetime.now(timezone.utc) - timedelta(seconds=20)
        mock_document_processing['created_at'] = created_time.isoformat()
        mock_get_doc.return_value = mock_document_processing

        response = client.get('/api/status/test-doc-123')

        assert response.status_code == 200
        data = response.json()

        assert data['status'] == 'processing'
        assert data['progress_stage'] == 'Converting document'
        assert data['progress'] > 10  # Should be more than queued
        assert data['progress'] < 95  # Cap at 95% until complete

    @patch('app.api.endpoints.status.supabase_service.get_document')
    async def test_get_status_processing_finalizing_stage(self, mock_get_doc, mock_document_processing):
        """Test status endpoint returns 'Finalizing...' for processing >= 100 seconds."""
        created_time = datetime.now(timezone.utc) - timedelta(seconds=120)
        mock_document_processing['created_at'] = created_time.isoformat()
        mock_get_doc.return_value = mock_document_processing

        response = client.get('/api/status/test-doc-123')

        assert response.status_code == 200
        data = response.json()

        assert data['status'] == 'processing'
        assert data['progress_stage'] == 'Finalizing...'
        assert data['elapsed_time'] >= 119

    @patch('app.api.endpoints.status.supabase_service.get_document')
    async def test_get_status_complete(self, mock_get_doc, mock_document_complete):
        """Test status endpoint for completed documents."""
        mock_get_doc.return_value = mock_document_complete

        response = client.get('/api/status/test-doc-123')

        assert response.status_code == 200
        data = response.json()

        assert data['status'] == 'complete'
        assert data['progress_stage'] == 'Processing complete'
        assert data['progress'] == 100
        assert data['completed_at'] is not None

    @patch('app.api.endpoints.status.supabase_service.get_document')
    async def test_get_status_failed(self, mock_get_doc, mock_document_failed):
        """Test status endpoint for failed documents."""
        mock_get_doc.return_value = mock_document_failed

        response = client.get('/api/status/test-doc-123')

        assert response.status_code == 200
        data = response.json()

        assert data['status'] == 'failed'
        assert data['progress_stage'] == 'Processing failed'
        assert data['progress'] == 0
        assert data['error_message'] == 'Processing failed: invalid file format'

    @patch('app.api.endpoints.status.supabase_service.get_document')
    async def test_progress_calculation_fast_mode(self, mock_get_doc, mock_document_processing):
        """Test progress calculation for fast mode without OCR."""
        # 15 seconds elapsed, fast mode = 30s base, no OCR
        # Expected: 10 + (15/30 * 80) = 10 + 40 = 50%
        created_time = datetime.now(timezone.utc) - timedelta(seconds=15)
        mock_document_processing['created_at'] = created_time.isoformat()
        mock_document_processing['processing_options'] = {
            'mode': 'fast',
            'ocr_enabled': False
        }
        mock_get_doc.return_value = mock_document_processing

        response = client.get('/api/status/test-doc-123')
        data = response.json()

        # Progress should be around 50%
        assert data['progress'] >= 45
        assert data['progress'] <= 55

    @patch('app.api.endpoints.status.supabase_service.get_document')
    async def test_progress_calculation_quality_mode_with_ocr(self, mock_get_doc, mock_document_processing):
        """Test progress calculation for quality mode with OCR."""
        # 90 seconds elapsed, quality mode = 90s base, with OCR = 90*2 = 180s total
        # Expected: 10 + (90/180 * 80) = 10 + 40 = 50%
        created_time = datetime.now(timezone.utc) - timedelta(seconds=90)
        mock_document_processing['created_at'] = created_time.isoformat()
        mock_document_processing['processing_options'] = {
            'mode': 'quality',
            'ocr_enabled': True
        }
        mock_get_doc.return_value = mock_document_processing

        response = client.get('/api/status/test-doc-123')
        data = response.json()

        # Progress should be around 50%
        assert data['progress'] >= 45
        assert data['progress'] <= 55

    @patch('app.api.endpoints.status.supabase_service.get_document')
    async def test_progress_capped_at_95_until_complete(self, mock_get_doc, mock_document_processing):
        """Test that progress is capped at 95% for processing status."""
        # Very long processing time to exceed estimate
        created_time = datetime.now(timezone.utc) - timedelta(seconds=200)
        mock_document_processing['created_at'] = created_time.isoformat()
        mock_get_doc.return_value = mock_document_processing

        response = client.get('/api/status/test-doc-123')
        data = response.json()

        assert data['progress'] <= 95
        assert data['status'] == 'processing'

    @patch('app.api.endpoints.status.supabase_service.get_document')
    async def test_elapsed_time_calculation(self, mock_get_doc, mock_document_processing):
        """Test elapsed time is calculated correctly."""
        created_time = datetime.now(timezone.utc) - timedelta(seconds=42)
        mock_document_processing['created_at'] = created_time.isoformat()
        mock_get_doc.return_value = mock_document_processing

        response = client.get('/api/status/test-doc-123')
        data = response.json()

        assert data['elapsed_time'] >= 41
        assert data['elapsed_time'] <= 44  # Allow small margin

    @patch('app.api.endpoints.status.supabase_service.get_document')
    async def test_document_not_found(self, mock_get_doc):
        """Test 404 response when document doesn't exist."""
        mock_get_doc.return_value = None

        response = client.get('/api/status/nonexistent-doc')

        assert response.status_code == 404
        assert response.json()['detail'] == 'Document not found'

    @patch('app.api.endpoints.status.supabase_service.get_document')
    async def test_enriched_response_format(self, mock_get_doc, mock_document_processing):
        """Test that response includes all enriched fields."""
        mock_get_doc.return_value = mock_document_processing

        response = client.get('/api/status/test-doc-123')

        assert response.status_code == 200
        data = response.json()

        # Check all required fields
        assert 'id' in data
        assert 'filename' in data
        assert 'status' in data
        assert 'processing_options' in data
        assert 'created_at' in data
        assert 'progress_stage' in data
        assert 'elapsed_time' in data
        assert 'progress' in data

        # Check progress_stage is a string
        assert isinstance(data['progress_stage'], str)
        assert len(data['progress_stage']) > 0

        # Check elapsed_time is an integer
        assert isinstance(data['elapsed_time'], int)
        assert data['elapsed_time'] >= 0

        # Check progress is an integer between 0 and 100
        assert isinstance(data['progress'], int)
        assert 0 <= data['progress'] <= 100

    @patch('app.api.endpoints.status.supabase_service.get_document')
    async def test_processing_options_included(self, mock_get_doc, mock_document_processing):
        """Test that processing options are included in response."""
        mock_document_processing['processing_options'] = {
            'mode': 'quality',
            'ocr_enabled': True
        }
        mock_get_doc.return_value = mock_document_processing

        response = client.get('/api/status/test-doc-123')
        data = response.json()

        assert data['processing_options']['mode'] == 'quality'
        assert data['processing_options']['ocr_enabled'] is True

    @patch('app.api.endpoints.status.supabase_service.get_document')
    @patch('app.api.endpoints.status.supabase_service.get_file_url')
    async def test_download_url_for_complete_document(self, mock_get_url, mock_get_doc, mock_document_complete):
        """Test that download URL is generated for completed documents."""
        mock_get_doc.return_value = mock_document_complete
        mock_get_url.return_value = 'https://storage.example.com/processed/test-doc-123/test.md'

        response = client.get('/api/status/test-doc-123')
        data = response.json()

        assert data['status'] == 'complete'
        assert data['download_url'] is not None
        assert 'test.md' in data['download_url']

    @patch('app.api.endpoints.status.supabase_service.get_document')
    async def test_no_download_url_for_incomplete_document(self, mock_get_doc, mock_document_processing):
        """Test that download URL is not generated for incomplete documents."""
        mock_get_doc.return_value = mock_document_processing

        response = client.get('/api/status/test-doc-123')
        data = response.json()

        assert data['status'] == 'processing'
        assert data.get('download_url') is None

    @patch('app.api.endpoints.status.supabase_service.get_document')
    async def test_handles_missing_created_at(self, mock_get_doc, mock_document_processing):
        """Test graceful handling when created_at is missing."""
        mock_document_processing['created_at'] = None
        mock_get_doc.return_value = mock_document_processing

        response = client.get('/api/status/test-doc-123')

        assert response.status_code == 200
        data = response.json()
        # Should still return a response, elapsed_time might be None
        assert data['status'] == 'processing'

    @patch('app.api.endpoints.status.supabase_service.get_document')
    async def test_handles_missing_processing_options(self, mock_get_doc, mock_document_processing):
        """Test graceful handling when processing_options is missing."""
        mock_document_processing['processing_options'] = None
        mock_get_doc.return_value = mock_document_processing

        response = client.get('/api/status/test-doc-123')

        assert response.status_code == 200
        data = response.json()
        # Should still calculate progress with default options
        assert data['progress'] >= 0
        assert data['progress'] <= 100
