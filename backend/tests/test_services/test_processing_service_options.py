"""
Tests for processing service with processing options.
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from app.services.processing_service import ProcessingService
import tempfile
import os


@pytest.fixture
def processing_service():
    """Create a processing service instance for testing."""
    return ProcessingService()


@pytest.mark.asyncio
async def test_process_document_with_default_options(processing_service):
    """Test processing document with default options (OCR off, fast mode)."""
    document_id = "test-doc-id"
    filename = "test.pdf"
    processing_options = {
        "ocr_enabled": False,
        "processing_mode": "fast"
    }
    
    with patch('app.services.processing_service.supabase_service') as mock_supabase, \
         patch('app.services.processing_service.DocumentConverter') as mock_converter:
        
        # Mock Supabase operations
        mock_supabase.update_document_status = AsyncMock()
        mock_supabase.download_file = AsyncMock(return_value=b"PDF content")
        mock_supabase.upload_file = AsyncMock()
        
        # Mock Docling converter
        mock_result = Mock()
        mock_result.document.export_to_markdown.return_value = "# Markdown content"
        mock_converter_instance = Mock()
        mock_converter_instance.convert.return_value = mock_result
        mock_converter.return_value = mock_converter_instance
        
        # Process document
        result = await processing_service.process_document(
            document_id, filename, processing_options
        )
        
        # Verify converter was called with correct options
        assert mock_converter.called
        call_args = mock_converter.call_args
        assert "format_options" in call_args[1]
        
        # Verify status updates
        assert mock_supabase.update_document_status.call_count >= 2


@pytest.mark.asyncio
async def test_process_document_with_ocr_enabled(processing_service):
    """Test processing document with OCR enabled."""
    document_id = "test-doc-id"
    filename = "test.pdf"
    processing_options = {
        "ocr_enabled": True,
        "processing_mode": "fast"
    }
    
    with patch('app.services.processing_service.supabase_service') as mock_supabase, \
         patch('app.services.processing_service.DocumentConverter') as mock_converter, \
         patch('app.services.processing_service.PdfPipelineOptions') as mock_pipeline:
        
        # Mock Supabase operations
        mock_supabase.update_document_status = AsyncMock()
        mock_supabase.download_file = AsyncMock(return_value=b"PDF content")
        mock_supabase.upload_file = AsyncMock()
        
        # Mock pipeline options
        mock_pipeline_instance = Mock()
        mock_pipeline.return_value = mock_pipeline_instance
        
        # Mock Docling converter
        mock_result = Mock()
        mock_result.document.export_to_markdown.return_value = "# Markdown content"
        mock_converter_instance = Mock()
        mock_converter_instance.convert.return_value = mock_result
        mock_converter.return_value = mock_converter_instance
        
        # Process document
        result = await processing_service.process_document(
            document_id, filename, processing_options
        )
        
        # Verify OCR was enabled in pipeline options
        assert mock_pipeline_instance.do_ocr == True


@pytest.mark.asyncio
async def test_process_document_with_quality_mode(processing_service):
    """Test processing document with quality mode."""
    document_id = "test-doc-id"
    filename = "test.pdf"
    processing_options = {
        "ocr_enabled": False,
        "processing_mode": "quality"
    }
    
    with patch('app.services.processing_service.supabase_service') as mock_supabase, \
         patch('app.services.processing_service.DocumentConverter') as mock_converter, \
         patch('app.services.processing_service.PdfPipelineOptions') as mock_pipeline:
        
        # Mock Supabase operations
        mock_supabase.update_document_status = AsyncMock()
        mock_supabase.download_file = AsyncMock(return_value=b"PDF content")
        mock_supabase.upload_file = AsyncMock()
        
        # Mock pipeline options
        mock_pipeline_instance = Mock()
        mock_pipeline.return_value = mock_pipeline_instance
        
        # Mock Docling converter
        mock_result = Mock()
        mock_result.document.export_to_markdown.return_value = "# Markdown content"
        mock_converter_instance = Mock()
        mock_converter_instance.convert.return_value = mock_result
        mock_converter.return_value = mock_converter_instance
        
        # Process document
        result = await processing_service.process_document(
            document_id, filename, processing_options
        )
        
        # Verify table structure analysis is enabled for quality mode
        assert mock_pipeline_instance.do_table_structure == True


@pytest.mark.asyncio
async def test_process_document_with_ocr_and_quality(processing_service):
    """Test processing document with both OCR and quality mode."""
    document_id = "test-doc-id"
    filename = "test.pdf"
    processing_options = {
        "ocr_enabled": True,
        "processing_mode": "quality"
    }
    
    with patch('app.services.processing_service.supabase_service') as mock_supabase, \
         patch('app.services.processing_service.DocumentConverter') as mock_converter, \
         patch('app.services.processing_service.PdfPipelineOptions') as mock_pipeline:
        
        # Mock Supabase operations
        mock_supabase.update_document_status = AsyncMock()
        mock_supabase.download_file = AsyncMock(return_value=b"PDF content")
        mock_supabase.upload_file = AsyncMock()
        
        # Mock pipeline options
        mock_pipeline_instance = Mock()
        mock_pipeline.return_value = mock_pipeline_instance
        
        # Mock Docling converter
        mock_result = Mock()
        mock_result.document.export_to_markdown.return_value = "# Markdown content"
        mock_converter_instance = Mock()
        mock_converter_instance.convert.return_value = mock_result
        mock_converter.return_value = mock_converter_instance
        
        # Process document
        result = await processing_service.process_document(
            document_id, filename, processing_options
        )
        
        # Verify both OCR and table structure are enabled
        assert mock_pipeline_instance.do_ocr == True
        assert mock_pipeline_instance.do_table_structure == True


@pytest.mark.asyncio
async def test_process_document_fast_mode_disables_table_structure(processing_service):
    """Test that fast mode disables table structure analysis."""
    document_id = "test-doc-id"
    filename = "test.pdf"
    processing_options = {
        "ocr_enabled": False,
        "processing_mode": "fast"
    }
    
    with patch('app.services.processing_service.supabase_service') as mock_supabase, \
         patch('app.services.processing_service.DocumentConverter') as mock_converter, \
         patch('app.services.processing_service.PdfPipelineOptions') as mock_pipeline:
        
        # Mock Supabase operations
        mock_supabase.update_document_status = AsyncMock()
        mock_supabase.download_file = AsyncMock(return_value=b"PDF content")
        mock_supabase.upload_file = AsyncMock()
        
        # Mock pipeline options
        mock_pipeline_instance = Mock()
        mock_pipeline.return_value = mock_pipeline_instance
        
        # Mock Docling converter
        mock_result = Mock()
        mock_result.document.export_to_markdown.return_value = "# Markdown content"
        mock_converter_instance = Mock()
        mock_converter_instance.convert.return_value = mock_result
        mock_converter.return_value = mock_converter_instance
        
        # Process document
        result = await processing_service.process_document(
            document_id, filename, processing_options
        )
        
        # Verify table structure is disabled for fast mode
        assert mock_pipeline_instance.do_table_structure == False


@pytest.mark.asyncio
async def test_process_document_handles_missing_options(processing_service):
    """Test processing document with missing processing options uses defaults."""
    document_id = "test-doc-id"
    filename = "test.pdf"
    processing_options = {}  # Empty options
    
    with patch('app.services.processing_service.supabase_service') as mock_supabase, \
         patch('app.services.processing_service.DocumentConverter') as mock_converter, \
         patch('app.services.processing_service.PdfPipelineOptions') as mock_pipeline:
        
        # Mock Supabase operations
        mock_supabase.update_document_status = AsyncMock()
        mock_supabase.download_file = AsyncMock(return_value=b"PDF content")
        mock_supabase.upload_file = AsyncMock()
        
        # Mock pipeline options
        mock_pipeline_instance = Mock()
        mock_pipeline.return_value = mock_pipeline_instance
        
        # Mock Docling converter
        mock_result = Mock()
        mock_result.document.export_to_markdown.return_value = "# Markdown content"
        mock_converter_instance = Mock()
        mock_converter_instance.convert.return_value = mock_result
        mock_converter.return_value = mock_converter_instance
        
        # Process document
        result = await processing_service.process_document(
            document_id, filename, processing_options
        )
        
        # Verify defaults are used (OCR off, fast mode)
        assert mock_pipeline_instance.do_ocr == False
        assert mock_pipeline_instance.do_table_structure == False


@pytest.mark.asyncio
async def test_process_document_updates_status_on_error(processing_service):
    """Test that document status is updated to failed on processing error."""
    document_id = "test-doc-id"
    filename = "test.pdf"
    processing_options = {
        "ocr_enabled": False,
        "processing_mode": "fast"
    }
    
    with patch('app.services.processing_service.supabase_service') as mock_supabase, \
         patch('app.services.processing_service.DocumentConverter') as mock_converter:
        
        # Mock Supabase operations
        mock_supabase.update_document_status = AsyncMock()
        mock_supabase.download_file = AsyncMock(return_value=b"PDF content")
        
        # Mock Docling converter to raise an error
        mock_converter_instance = Mock()
        mock_converter_instance.convert.side_effect = Exception("Processing error")
        mock_converter.return_value = mock_converter_instance
        
        # Process document and expect exception
        with pytest.raises(Exception):
            await processing_service.process_document(
                document_id, filename, processing_options
            )
        
        # Verify status was updated to failed
        calls = mock_supabase.update_document_status.call_args_list
        assert any('failed' in str(call) for call in calls)