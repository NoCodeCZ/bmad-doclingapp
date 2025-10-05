"""
Tests for upload endpoint with processing options.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
import io

client = TestClient(app)


def test_upload_with_default_processing_options():
    """Test upload with default processing options (ocr_enabled=False, processing_mode='fast')."""
    file_content = b"Test PDF content"
    files = {"file": ("test.pdf", io.BytesIO(file_content), "application/pdf")}
    
    response = client.post("/api/upload", files=files)
    
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["filename"] == "test.pdf"
    assert data["status"] == "queued"


def test_upload_with_ocr_enabled():
    """Test upload with OCR enabled."""
    file_content = b"Test PDF content"
    files = {"file": ("test.pdf", io.BytesIO(file_content), "application/pdf")}
    data = {"ocr_enabled": "true"}
    
    response = client.post("/api/upload", files=files, data=data)
    
    assert response.status_code == 200
    result = response.json()
    assert result["status"] == "queued"


def test_upload_with_quality_mode():
    """Test upload with quality processing mode."""
    file_content = b"Test PDF content"
    files = {"file": ("test.pdf", io.BytesIO(file_content), "application/pdf")}
    data = {"processing_mode": "quality"}
    
    response = client.post("/api/upload", files=files, data=data)
    
    assert response.status_code == 200
    result = response.json()
    assert result["status"] == "queued"


def test_upload_with_ocr_and_quality_mode():
    """Test upload with both OCR enabled and quality mode."""
    file_content = b"Test PDF content"
    files = {"file": ("test.pdf", io.BytesIO(file_content), "application/pdf")}
    data = {
        "ocr_enabled": "true",
        "processing_mode": "quality"
    }
    
    response = client.post("/api/upload", files=files, data=data)
    
    assert response.status_code == 200
    result = response.json()
    assert result["status"] == "queued"


def test_upload_with_invalid_processing_mode():
    """Test upload with invalid processing mode."""
    file_content = b"Test PDF content"
    files = {"file": ("test.pdf", io.BytesIO(file_content), "application/pdf")}
    data = {"processing_mode": "invalid_mode"}
    
    response = client.post("/api/upload", files=files, data=data)
    
    assert response.status_code == 400
    result = response.json()
    assert "Invalid processing mode" in result["detail"]


def test_upload_with_fast_mode_explicitly():
    """Test upload with fast mode explicitly set."""
    file_content = b"Test PDF content"
    files = {"file": ("test.pdf", io.BytesIO(file_content), "application/pdf")}
    data = {"processing_mode": "fast"}
    
    response = client.post("/api/upload", files=files, data=data)
    
    assert response.status_code == 200
    result = response.json()
    assert result["status"] == "queued"


def test_upload_with_ocr_false_explicitly():
    """Test upload with OCR explicitly disabled."""
    file_content = b"Test PDF content"
    files = {"file": ("test.pdf", io.BytesIO(file_content), "application/pdf")}
    data = {"ocr_enabled": "false"}
    
    response = client.post("/api/upload", files=files, data=data)
    
    assert response.status_code == 200
    result = response.json()
    assert result["status"] == "queued"


def test_upload_docx_with_processing_options():
    """Test uploading DOCX file with processing options."""
    file_content = b"Test DOCX content"
    files = {"file": ("test.docx", io.BytesIO(file_content), "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
    data = {
        "ocr_enabled": "true",
        "processing_mode": "quality"
    }
    
    response = client.post("/api/upload", files=files, data=data)
    
    assert response.status_code == 200
    result = response.json()
    assert result["filename"] == "test.docx"


def test_upload_pptx_with_processing_options():
    """Test uploading PPTX file with processing options."""
    file_content = b"Test PPTX content"
    files = {"file": ("test.pptx", io.BytesIO(file_content), "application/vnd.openxmlformats-officedocument.presentationml.presentation")}
    data = {
        "ocr_enabled": "false",
        "processing_mode": "fast"
    }
    
    response = client.post("/api/upload", files=files, data=data)
    
    assert response.status_code == 200
    result = response.json()
    assert result["filename"] == "test.pptx"


def test_upload_xlsx_with_processing_options():
    """Test uploading XLSX file with processing options."""
    file_content = b"Test XLSX content"
    files = {"file": ("test.xlsx", io.BytesIO(file_content), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
    data = {
        "processing_mode": "quality"
    }
    
    response = client.post("/api/upload", files=files, data=data)
    
    assert response.status_code == 200
    result = response.json()
    assert result["filename"] == "test.xlsx"


def test_upload_with_case_sensitive_processing_mode():
    """Test that processing mode validation is case-sensitive."""
    file_content = b"Test PDF content"
    files = {"file": ("test.pdf", io.BytesIO(file_content), "application/pdf")}
    data = {"processing_mode": "Fast"}  # Capitalized
    
    response = client.post("/api/upload", files=files, data=data)
    
    # Should fail because it's case-sensitive
    assert response.status_code == 400
    result = response.json()
    assert "Invalid processing mode" in result["detail"]


def test_upload_rejects_unsupported_file_type_with_options():
    """Test that unsupported file types are rejected even with valid processing options."""
    file_content = b"Test TXT content"
    files = {"file": ("test.txt", io.BytesIO(file_content), "text/plain")}
    data = {
        "ocr_enabled": "true",
        "processing_mode": "quality"
    }
    
    response = client.post("/api/upload", files=files, data=data)
    
    assert response.status_code == 400
    result = response.json()
    assert "Unsupported file type" in result["detail"]