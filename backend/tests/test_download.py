"""
Tests for download endpoint functionality.

Implements comprehensive test coverage for:
- Valid document downloads
- Error scenarios (file not found, storage access failures)
- Filename cleaning and sanitization
- Content-disposition headers
- MIME type handling
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch, MagicMock
from app.main import app

client = TestClient(app)


class TestDownloadEndpoint:
    """Test suite for /api/download/{document_id} endpoint."""

    @pytest.fixture
    def mock_document(self):
        """Mock complete document record."""
        return {
            'id': 'test-doc-123',
            'filename': 'sample_report.pdf',
            'status': 'complete',
            'processing_options': {
                'mode': 'fast',
                'ocr_enabled': False
            },
            'created_at': '2025-10-06T00:00:00Z',
            'completed_at': '2025-10-06T00:01:00Z',
            'error_message': None
        }

    @pytest.fixture
    def mock_file_content(self):
        """Mock processed markdown file content."""
        return b"# Sample Report\n\nThis is a test document.\n\n## Section 1\n\nContent here."

    @patch('app.api.endpoints.download.supabase_service')
    def test_download_valid_document(self, mock_supabase, mock_document, mock_file_content):
        """
        Test successful download of a completed document.

        Verifies:
        - Status code 200
        - Correct Content-Type header
        - Proper Content-Disposition with cleaned filename
        - File content matches expected
        - Content-Length header is set
        """
        # Setup mocks
        mock_supabase.get_document = AsyncMock(return_value=mock_document)
        mock_supabase.download_file = AsyncMock(return_value=mock_file_content)

        # Make request
        response = client.get('/api/download/test-doc-123')

        # Assertions
        assert response.status_code == 200
        assert response.headers['content-type'] == 'text/markdown; charset=utf-8'
        assert 'attachment' in response.headers['content-disposition']
        assert 'sample_report.md' in response.headers['content-disposition']
        assert response.headers['content-length'] == str(len(mock_file_content))
        assert response.content == mock_file_content

        # Verify service calls
        mock_supabase.get_document.assert_called_once_with('test-doc-123')
        mock_supabase.download_file.assert_called_once()

    @patch('app.api.endpoints.download.supabase_service')
    def test_download_document_not_found(self, mock_supabase):
        """
        Test download attempt for non-existent document.

        Verifies:
        - Status code 404
        - User-friendly error message
        - Proper error detail structure
        """
        # Setup mock to return None (document not found)
        mock_supabase.get_document = AsyncMock(return_value=None)

        # Make request
        response = client.get('/api/download/nonexistent-doc')

        # Assertions
        assert response.status_code == 404
        assert 'detail' in response.json()
        assert 'file may have been moved or deleted' in response.json()['detail'].lower()
        assert 'process document again' in response.json()['detail'].lower()

    @patch('app.api.endpoints.download.supabase_service')
    def test_download_document_not_complete(self, mock_supabase):
        """
        Test download attempt for document still processing.

        Verifies:
        - Status code 400
        - Error message indicates document not ready
        - Current status included in error message
        """
        # Setup mock with processing document
        mock_supabase.get_document = AsyncMock(return_value={
            'id': 'test-doc-456',
            'filename': 'processing.pdf',
            'status': 'processing',
            'processing_options': {'mode': 'fast', 'ocr_enabled': False}
        })

        # Make request
        response = client.get('/api/download/test-doc-456')

        # Assertions
        assert response.status_code == 400
        assert 'detail' in response.json()
        assert 'not ready for download' in response.json()['detail'].lower()
        assert 'processing' in response.json()['detail'].lower()

    @patch('app.api.endpoints.download.supabase_service')
    def test_download_storage_error(self, mock_supabase, mock_document):
        """
        Test handling of storage access errors.

        Verifies:
        - Status code 500
        - User-friendly error message
        - Error is logged (implicitly via exception)
        """
        # Setup mocks
        mock_supabase.get_document = AsyncMock(return_value=mock_document)
        mock_supabase.download_file = AsyncMock(
            side_effect=Exception("Storage bucket not accessible")
        )

        # Make request
        response = client.get('/api/download/test-doc-123')

        # Assertions
        assert response.status_code == 500
        assert 'detail' in response.json()
        assert 'file may have been moved or deleted' in response.json()['detail'].lower()

    @patch('app.api.endpoints.download.supabase_service')
    def test_download_filename_cleaning(self, mock_supabase, mock_file_content):
        """
        Test filename cleaning with special characters.

        Verifies:
        - Special characters are removed/replaced
        - Extension is changed to .md
        - Filename is safe for cross-platform use
        """
        # Setup mock with problematic filename
        mock_supabase.get_document = AsyncMock(return_value={
            'id': 'test-doc-789',
            'filename': 'My <Report> 2024: Q1.pdf',
            'status': 'complete',
            'processing_options': {'mode': 'fast', 'ocr_enabled': False}
        })
        mock_supabase.download_file = AsyncMock(return_value=mock_file_content)

        # Make request
        response = client.get('/api/download/test-doc-789')

        # Assertions
        assert response.status_code == 200
        content_disposition = response.headers['content-disposition']

        # Verify special characters are cleaned
        assert '<' not in content_disposition
        assert '>' not in content_disposition
        assert ':' not in content_disposition
        assert '.md' in content_disposition

    @patch('app.api.endpoints.download.supabase_service')
    def test_download_path_traversal_prevention(self, mock_supabase, mock_file_content):
        """
        Test prevention of path traversal attacks in filename.

        Verifies:
        - Path separators are removed
        - Directory traversal attempts are neutralized
        - Filename is sanitized for security
        """
        # Setup mock with path traversal attempt
        mock_supabase.get_document = AsyncMock(return_value={
            'id': 'test-doc-999',
            'filename': '../../../etc/passwd.pdf',
            'status': 'complete',
            'processing_options': {'mode': 'fast', 'ocr_enabled': False}
        })
        mock_supabase.download_file = AsyncMock(return_value=mock_file_content)

        # Make request
        response = client.get('/api/download/test-doc-999')

        # Assertions
        assert response.status_code == 200
        content_disposition = response.headers['content-disposition']

        # Verify path traversal is prevented
        assert '..' not in content_disposition
        assert '/' not in content_disposition or content_disposition.count('/') == 0
        assert '\\' not in content_disposition

    @patch('app.api.endpoints.download.supabase_service')
    def test_download_various_file_extensions(self, mock_supabase, mock_file_content):
        """
        Test filename cleaning for various document types.

        Verifies:
        - .pdf, .docx, .pptx, .xlsx all convert to .md
        - Original filename is preserved (minus extension)
        """
        test_cases = [
            ('report.pdf', 'report.md'),
            ('presentation.pptx', 'presentation.md'),
            ('spreadsheet.xlsx', 'spreadsheet.md'),
            ('document.docx', 'document.md'),
        ]

        for original_filename, expected_md_filename in test_cases:
            # Setup mock
            mock_supabase.get_document = AsyncMock(return_value={
                'id': f'test-{original_filename}',
                'filename': original_filename,
                'status': 'complete',
                'processing_options': {'mode': 'fast', 'ocr_enabled': False}
            })
            mock_supabase.download_file = AsyncMock(return_value=mock_file_content)

            # Make request
            response = client.get(f'/api/download/test-{original_filename}')

            # Assertions
            assert response.status_code == 200
            assert expected_md_filename in response.headers['content-disposition']

    @patch('app.api.endpoints.download.supabase_service')
    def test_download_security_headers(self, mock_supabase, mock_document, mock_file_content):
        """
        Test presence of security headers in download response.

        Verifies:
        - X-Content-Type-Options is set to nosniff
        - Cache-Control is set appropriately
        - Content-Type is correct
        """
        # Setup mocks
        mock_supabase.get_document = AsyncMock(return_value=mock_document)
        mock_supabase.download_file = AsyncMock(return_value=mock_file_content)

        # Make request
        response = client.get('/api/download/test-doc-123')

        # Assertions
        assert response.status_code == 200
        assert response.headers['x-content-type-options'] == 'nosniff'
        assert 'no-cache' in response.headers['cache-control']
        assert response.headers['content-type'] == 'text/markdown; charset=utf-8'

    @patch('app.api.endpoints.download.supabase_service')
    def test_download_content_length_header(self, mock_supabase, mock_document, mock_file_content):
        """
        Test Content-Length header is correctly set.

        Verifies:
        - Content-Length matches actual file size
        - Header is present in response
        """
        # Setup mocks
        mock_supabase.get_document = AsyncMock(return_value=mock_document)
        mock_supabase.download_file = AsyncMock(return_value=mock_file_content)

        # Make request
        response = client.get('/api/download/test-doc-123')

        # Assertions
        assert response.status_code == 200
        assert 'content-length' in response.headers
        assert int(response.headers['content-length']) == len(mock_file_content)

    @patch('app.api.endpoints.download.supabase_service')
    def test_download_empty_filename_fallback(self, mock_supabase, mock_file_content):
        """
        Test fallback filename when cleaning results in empty string.

        Verifies:
        - Empty filename uses 'document.md' fallback
        - Download still succeeds
        """
        # Setup mock with filename that cleans to empty
        mock_supabase.get_document = AsyncMock(return_value={
            'id': 'test-doc-empty',
            'filename': '....',
            'status': 'complete',
            'processing_options': {'mode': 'fast', 'ocr_enabled': False}
        })
        mock_supabase.download_file = AsyncMock(return_value=mock_file_content)

        # Make request
        response = client.get('/api/download/test-doc-empty')

        # Assertions
        assert response.status_code == 200
        assert 'document.md' in response.headers['content-disposition']


class TestFilenameUtils:
    """Test suite for filename cleaning utilities."""

    def test_clean_filename_basic(self):
        """Test basic filename cleaning."""
        from app.utils.filename_utils import clean_filename

        result = clean_filename('report.pdf')
        assert result == 'report.md'

    def test_clean_filename_special_chars(self):
        """Test cleaning of special characters."""
        from app.utils.filename_utils import clean_filename

        result = clean_filename('my<file>name:test.pdf')
        assert '<' not in result
        assert '>' not in result
        assert ':' not in result
        assert result.endswith('.md')

    def test_clean_filename_path_traversal(self):
        """Test prevention of path traversal."""
        from app.utils.filename_utils import clean_filename

        result = clean_filename('../../../etc/passwd.pdf')
        assert '..' not in result
        assert '/' not in result or result.count('/') == 0

    def test_clean_filename_spaces(self):
        """Test space replacement with underscores."""
        from app.utils.filename_utils import clean_filename

        result = clean_filename('my document name.pdf')
        assert ' ' not in result
        assert '_' in result
        assert result == 'my_document_name.md'

    def test_validate_filename_valid(self):
        """Test validation of valid filenames."""
        from app.utils.filename_utils import validate_filename

        assert validate_filename('document.md') is True
        assert validate_filename('report_2024.md') is True

    def test_validate_filename_invalid(self):
        """Test validation rejects invalid filenames."""
        from app.utils.filename_utils import validate_filename

        assert validate_filename('') is False
        assert validate_filename('file/with/slashes.md') is False
        assert validate_filename('../traversal.md') is False
        assert validate_filename('a' * 300 + '.md') is False

    def test_get_safe_filename_fallback(self):
        """Test safe filename with fallback."""
        from app.utils.filename_utils import get_safe_filename

        result = get_safe_filename('normal.pdf')
        assert result == 'normal.md'

        # Test fallback for invalid filename
        result = get_safe_filename('')
        assert result == 'document.md'
