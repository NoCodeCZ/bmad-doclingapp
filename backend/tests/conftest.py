"""
Pytest configuration and fixtures for integration and unit tests.
"""
import pytest
import os
import asyncio
from typing import Generator, AsyncGenerator
from unittest.mock import MagicMock, AsyncMock
from fastapi.testclient import TestClient
from app.main import app


# Test Configuration
class IntegrationTestConfig:
    """Configuration for integration tests."""

    # Test database configuration
    TEST_DATABASE_URL = os.getenv(
        "TEST_DATABASE_URL",
        "postgresql://test_user:test_pass@localhost:5432/test_docling"
    )

    # Mock service configuration
    MOCK_SUPABASE = True
    MOCK_DOCLING = True

    # Test file paths
    TEST_FIXTURES_DIR = os.path.join(
        os.path.dirname(__file__),
        "fixtures",
        "integration"
    )

    # Performance thresholds
    MAX_PROCESSING_TIME_FAST = 60  # seconds
    MAX_PROCESSING_TIME_QUALITY = 180  # seconds
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

    # Success rate thresholds
    MIN_SUCCESS_RATE = 0.95  # 95%
    MAX_ERROR_RATE = 0.05  # 5%


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
def test_client() -> Generator[TestClient, None, None]:
    """Create a test client for FastAPI application."""
    with TestClient(app) as client:
        yield client


@pytest.fixture(scope="function")
def integration_config() -> IntegrationTestConfig:
    """Provide integration test configuration."""
    return IntegrationTestConfig()


@pytest.fixture(scope="function")
def mock_supabase_client():
    """Create a mock Supabase client for testing."""
    mock_client = MagicMock()
    mock_client.table = MagicMock()
    mock_client.storage = MagicMock()
    return mock_client


@pytest.fixture(scope="function")
def mock_docling_service():
    """Create a mock Docling service for testing."""
    mock_service = AsyncMock()
    mock_service.convert_document = AsyncMock()
    return mock_service


@pytest.fixture(scope="function")
def test_document_data():
    """Provide sample document data for testing."""
    return {
        'id': 'test-doc-123',
        'filename': 'test-document.pdf',
        'status': 'queued',
        'processing_options': {
            'mode': 'fast',
            'ocr_enabled': False
        },
        'created_at': '2025-10-06T12:00:00Z',
        'completed_at': None,
        'error_message': None
    }


@pytest.fixture
def test_fixtures_dir(integration_config) -> str:
    """Return path to test fixtures directory."""
    return integration_config.TEST_FIXTURES_DIR


@pytest.fixture
def sample_pdf_path(test_fixtures_dir) -> str:
    """Return path to sample PDF file."""
    return os.path.join(test_fixtures_dir, "simple_document.pdf")


@pytest.fixture
def sample_docx_path(test_fixtures_dir) -> str:
    """Return path to sample DOCX file."""
    return os.path.join(test_fixtures_dir, "simple_document.docx")


@pytest.fixture
def sample_pptx_path(test_fixtures_dir) -> str:
    """Return path to sample PPTX file."""
    return os.path.join(test_fixtures_dir, "simple_presentation.pptx")


@pytest.fixture
def sample_xlsx_path(test_fixtures_dir) -> str:
    """Return path to sample XLSX file."""
    return os.path.join(test_fixtures_dir, "simple_spreadsheet.xlsx")


@pytest.fixture
def complex_pdf_path(test_fixtures_dir) -> str:
    """Return path to complex PDF with tables."""
    return os.path.join(test_fixtures_dir, "complex_document.pdf")


@pytest.fixture
def scanned_pdf_path(test_fixtures_dir) -> str:
    """Return path to scanned PDF for OCR testing."""
    return os.path.join(test_fixtures_dir, "scanned_document.pdf")


@pytest.fixture
def oversized_file_path(test_fixtures_dir) -> str:
    """Return path to oversized file (11MB+)."""
    return os.path.join(test_fixtures_dir, "oversized_document.pdf")


@pytest.fixture
def corrupted_file_path(test_fixtures_dir) -> str:
    """Return path to corrupted file."""
    return os.path.join(test_fixtures_dir, "corrupted_document.pdf")


@pytest.fixture
def unsupported_file_path(test_fixtures_dir) -> str:
    """Return path to unsupported file format."""
    return os.path.join(test_fixtures_dir, "unsupported_file.txt")


@pytest.fixture(scope="function")
async def cleanup_test_documents():
    """Cleanup test documents after test execution."""
    document_ids = []

    def register_document(doc_id: str):
        document_ids.append(doc_id)

    yield register_document

    # Cleanup after test
    # In a real scenario, this would delete from database
    # For now, we just track them
    document_ids.clear()


# Performance tracking fixtures
@pytest.fixture
def performance_tracker():
    """Track performance metrics during tests."""
    metrics = {
        'processing_times': [],
        'file_types': [],
        'modes': [],
        'success_count': 0,
        'failure_count': 0
    }

    def record_processing(file_type: str, mode: str, time_taken: float, success: bool):
        metrics['processing_times'].append(time_taken)
        metrics['file_types'].append(file_type)
        metrics['modes'].append(mode)
        if success:
            metrics['success_count'] += 1
        else:
            metrics['failure_count'] += 1

    def get_metrics():
        return metrics

    return {
        'record': record_processing,
        'get_metrics': get_metrics
    }


# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "staging: mark test as staging environment test"
    )
    config.addinivalue_line(
        "markers", "performance: mark test as performance benchmark"
    )
    config.addinivalue_line(
        "markers", "error_scenario: mark test as error scenario test"
    )
