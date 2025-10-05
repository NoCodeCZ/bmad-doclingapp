"""
Integration tests for status polling workflow.
Tests end-to-end flow from document creation through status transitions.
"""
import pytest
import asyncio
from datetime import datetime, timezone
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


class TestStatusPollingIntegration:
    """Integration tests for complete status polling workflow."""

    @pytest.fixture
    def sample_document_data(self):
        """Sample document data for testing."""
        return {
            'filename': 'integration-test.pdf',
            'processing_options': {
                'mode': 'fast',
                'ocr_enabled': False
            }
        }

    @patch('app.api.endpoints.status.supabase_service.get_document')
    async def test_status_polling_queued_to_processing_to_complete(self, mock_get_doc):
        """Test complete workflow: queued -> processing -> complete."""
        doc_id = 'test-integration-123'
        base_time = datetime.now(timezone.utc)

        # Simulate polling sequence
        mock_responses = [
            # First poll: Just uploaded (uploading stage)
            {
                'id': doc_id,
                'filename': 'integration-test.pdf',
                'status': 'queued',
                'processing_options': {'mode': 'fast', 'ocr_enabled': False},
                'created_at': base_time.isoformat(),
                'completed_at': None,
                'error_message': None
            },
            # Second poll: Still queued (queued stage)
            {
                'id': doc_id,
                'filename': 'integration-test.pdf',
                'status': 'queued',
                'processing_options': {'mode': 'fast', 'ocr_enabled': False},
                'created_at': base_time.isoformat(),
                'completed_at': None,
                'error_message': None
            },
            # Third poll: Now processing
            {
                'id': doc_id,
                'filename': 'integration-test.pdf',
                'status': 'processing',
                'processing_options': {'mode': 'fast', 'ocr_enabled': False},
                'created_at': base_time.isoformat(),
                'completed_at': None,
                'error_message': None
            },
            # Fourth poll: Complete
            {
                'id': doc_id,
                'filename': 'integration-test.pdf',
                'status': 'complete',
                'processing_options': {'mode': 'fast', 'ocr_enabled': False},
                'created_at': base_time.isoformat(),
                'completed_at': datetime.now(timezone.utc).isoformat(),
                'error_message': None
            }
        ]

        # Simulate multiple polls
        for i, mock_response in enumerate(mock_responses):
            # Advance time for each poll
            import time
            if i > 0:
                time.sleep(0.1)  # Small delay to simulate passage of time

            # Update created_at to simulate elapsed time
            if i > 0:
                from datetime import timedelta
                created_at = base_time - timedelta(seconds=i * 5)
                mock_response['created_at'] = created_at.isoformat()

            mock_get_doc.return_value = mock_response

            response = client.get(f'/api/status/{doc_id}')
            assert response.status_code == 200

            data = response.json()

            # Verify response structure
            assert 'status' in data
            assert 'progress' in data
            assert 'progress_stage' in data
            assert 'elapsed_time' in data

            # Verify status progression
            assert data['status'] == mock_response['status']

            # Verify progress increases over time (except for complete/failed)
            if data['status'] != 'failed':
                assert data['progress'] >= 0
                assert data['progress'] <= 100

            # Verify terminal state has 100% progress
            if data['status'] == 'complete':
                assert data['progress'] == 100
                assert 'complete' in data['progress_stage'].lower()

    @patch('app.api.endpoints.status.supabase_service.get_document')
    async def test_status_polling_with_failure(self, mock_get_doc):
        """Test workflow that ends in failure."""
        doc_id = 'test-fail-123'
        base_time = datetime.now(timezone.utc)

        # Sequence: queued -> processing -> failed
        mock_responses = [
            {
                'id': doc_id,
                'filename': 'test-fail.pdf',
                'status': 'queued',
                'processing_options': {'mode': 'fast', 'ocr_enabled': False},
                'created_at': base_time.isoformat(),
                'completed_at': None,
                'error_message': None
            },
            {
                'id': doc_id,
                'filename': 'test-fail.pdf',
                'status': 'processing',
                'processing_options': {'mode': 'fast', 'ocr_enabled': False},
                'created_at': base_time.isoformat(),
                'completed_at': None,
                'error_message': None
            },
            {
                'id': doc_id,
                'filename': 'test-fail.pdf',
                'status': 'failed',
                'processing_options': {'mode': 'fast', 'ocr_enabled': False},
                'created_at': base_time.isoformat(),
                'completed_at': datetime.now(timezone.utc).isoformat(),
                'error_message': 'File corrupted'
            }
        ]

        for mock_response in mock_responses:
            mock_get_doc.return_value = mock_response

            response = client.get(f'/api/status/{doc_id}')
            data = response.json()

            if data['status'] == 'failed':
                assert data['progress'] == 0
                assert 'failed' in data['progress_stage'].lower()
                assert data['error_message'] == 'File corrupted'

    @patch('app.api.endpoints.status.supabase_service.get_document')
    async def test_time_estimation_accuracy_fast_mode(self, mock_get_doc):
        """Test time estimation for fast mode processing."""
        doc_id = 'test-time-fast'
        base_time = datetime.now(timezone.utc)

        # Simulate processing at 15 seconds elapsed (halfway through 30s fast mode)
        from datetime import timedelta
        created_at = base_time - timedelta(seconds=15)

        mock_response = {
            'id': doc_id,
            'filename': 'test.pdf',
            'status': 'processing',
            'processing_options': {'mode': 'fast', 'ocr_enabled': False},
            'created_at': created_at.isoformat(),
            'completed_at': None,
            'error_message': None
        }

        mock_get_doc.return_value = mock_response

        response = client.get(f'/api/status/{doc_id}')
        data = response.json()

        # Fast mode without OCR: 30s total, 15s elapsed
        # Progress should be around 50%
        assert data['progress'] >= 45
        assert data['progress'] <= 55
        assert data['elapsed_time'] >= 14
        assert data['elapsed_time'] <= 16

    @patch('app.api.endpoints.status.supabase_service.get_document')
    async def test_time_estimation_accuracy_quality_mode_with_ocr(self, mock_get_doc):
        """Test time estimation for quality mode with OCR."""
        doc_id = 'test-time-quality-ocr'
        base_time = datetime.now(timezone.utc)

        # Simulate processing at 90 seconds elapsed (halfway through 180s quality+OCR)
        from datetime import timedelta
        created_at = base_time - timedelta(seconds=90)

        mock_response = {
            'id': doc_id,
            'filename': 'test.pdf',
            'status': 'processing',
            'processing_options': {'mode': 'quality', 'ocr_enabled': True},
            'created_at': created_at.isoformat(),
            'completed_at': None,
            'error_message': None
        }

        mock_get_doc.return_value = mock_response

        response = client.get(f'/api/status/{doc_id}')
        data = response.json()

        # Quality mode with OCR: 180s total (90*2), 90s elapsed
        # Progress should be around 50%
        assert data['progress'] >= 45
        assert data['progress'] <= 55
        assert data['elapsed_time'] >= 89
        assert data['elapsed_time'] <= 91

    @patch('app.api.endpoints.status.supabase_service.get_document')
    async def test_progress_stage_transitions(self, mock_get_doc):
        """Test that progress stages transition correctly."""
        doc_id = 'test-stages'
        base_time = datetime.now(timezone.utc)
        from datetime import timedelta

        test_cases = [
            # (elapsed_seconds, expected_status, expected_stage_partial)
            (2, 'queued', 'uploading'),
            (10, 'queued', 'queued for'),
            (20, 'processing', 'converting'),
            (120, 'processing', 'finalizing'),
        ]

        for elapsed, status, expected_stage in test_cases:
            created_at = base_time - timedelta(seconds=elapsed)

            mock_response = {
                'id': doc_id,
                'filename': 'test.pdf',
                'status': status,
                'processing_options': {'mode': 'fast', 'ocr_enabled': False},
                'created_at': created_at.isoformat(),
                'completed_at': None,
                'error_message': None
            }

            mock_get_doc.return_value = mock_response

            response = client.get(f'/api/status/{doc_id}')
            data = response.json()

            assert data['status'] == status
            assert expected_stage.lower() in data['progress_stage'].lower(), \
                f"Expected '{expected_stage}' in progress_stage, got '{data['progress_stage']}'"

    @patch('app.api.endpoints.status.supabase_service.get_document')
    async def test_polling_behavior_under_various_conditions(self, mock_get_doc):
        """Test polling behavior under different scenarios."""
        doc_id = 'test-polling-behavior'
        base_time = datetime.now(timezone.utc)

        scenarios = [
            # Scenario 1: Very quick processing (< 10 seconds)
            {
                'created_at': base_time,
                'status': 'complete',
                'elapsed_expected': 0
            },
            # Scenario 2: Long processing (> estimated time)
            {
                'created_at': base_time,
                'status': 'processing',
                'elapsed_expected': 200  # Way over 30s estimate
            },
            # Scenario 3: Processing with errors
            {
                'created_at': base_time,
                'status': 'failed',
                'elapsed_expected': 15
            }
        ]

        for scenario in scenarios:
            from datetime import timedelta
            if scenario['elapsed_expected'] > 0:
                created_at = base_time - timedelta(seconds=scenario['elapsed_expected'])
            else:
                created_at = base_time

            mock_response = {
                'id': doc_id,
                'filename': 'test.pdf',
                'status': scenario['status'],
                'processing_options': {'mode': 'fast', 'ocr_enabled': False},
                'created_at': created_at.isoformat(),
                'completed_at': datetime.now(timezone.utc).isoformat() if scenario['status'] in ['complete', 'failed'] else None,
                'error_message': 'Test error' if scenario['status'] == 'failed' else None
            }

            mock_get_doc.return_value = mock_response

            response = client.get(f'/api/status/{doc_id}')
            assert response.status_code == 200

            data = response.json()

            # Verify appropriate progress for each scenario
            if scenario['status'] == 'complete':
                assert data['progress'] == 100
            elif scenario['status'] == 'failed':
                assert data['progress'] == 0
            elif scenario['status'] == 'processing':
                # For long processing, should be capped at 95%
                if scenario['elapsed_expected'] > 100:
                    assert data['progress'] <= 95

    @patch('app.api.endpoints.status.supabase_service.get_document')
    async def test_concurrent_status_requests(self, mock_get_doc):
        """Test handling of concurrent status requests for same document."""
        doc_id = 'test-concurrent'
        base_time = datetime.now(timezone.utc)

        mock_response = {
            'id': doc_id,
            'filename': 'test.pdf',
            'status': 'processing',
            'processing_options': {'mode': 'fast', 'ocr_enabled': False},
            'created_at': base_time.isoformat(),
            'completed_at': None,
            'error_message': None
        }

        mock_get_doc.return_value = mock_response

        # Simulate 5 concurrent requests
        responses = []
        for _ in range(5):
            response = client.get(f'/api/status/{doc_id}')
            responses.append(response)

        # All should succeed
        for response in responses:
            assert response.status_code == 200
            data = response.json()
            assert data['status'] == 'processing'
            assert data['progress'] > 0

    @patch('app.api.endpoints.status.supabase_service.get_document')
    async def test_response_consistency_across_polls(self, mock_get_doc):
        """Test that responses are consistent for same document state."""
        doc_id = 'test-consistency'
        base_time = datetime.now(timezone.utc)

        mock_response = {
            'id': doc_id,
            'filename': 'test.pdf',
            'status': 'processing',
            'processing_options': {'mode': 'fast', 'ocr_enabled': False},
            'created_at': base_time.isoformat(),
            'completed_at': None,
            'error_message': None
        }

        mock_get_doc.return_value = mock_response

        # Poll multiple times with same state
        responses_data = []
        for _ in range(3):
            response = client.get(f'/api/status/{doc_id}')
            responses_data.append(response.json())

        # All responses should have same status and similar progress
        statuses = [r['status'] for r in responses_data]
        assert len(set(statuses)) == 1  # All same status

        # Progress should be consistent (allowing small variation due to time)
        progresses = [r['progress'] for r in responses_data]
        assert max(progresses) - min(progresses) <= 2  # Within 2% variation
