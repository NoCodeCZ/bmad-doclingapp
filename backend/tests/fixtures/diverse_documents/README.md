# Diverse Documents Test Fixtures

This directory contains test documents for comprehensive testing of the Workshop Document Processor across various document types, quality levels, and edge cases.

## Directory Structure

### PDF Documents

#### `pdf/clean_digital/`
Clean, digitally-created PDF files with clear text, tables, and formatting.
- **Characteristics**: High-quality text extraction, well-defined structure
- **Expected Behavior**: High success rate, fast processing, excellent markdown quality

#### `pdf/scanned_low_quality/`
Scanned PDF documents with low image quality (< 150 DPI).
- **Characteristics**: Poor image quality, requires OCR, may have artifacts
- **Expected Behavior**: OCR required, slower processing, potential quality degradation

#### `pdf/scanned_high_quality/`
Scanned PDF documents with high image quality (≥ 300 DPI).
- **Characteristics**: Good image quality, requires OCR, clear text
- **Expected Behavior**: OCR required, moderate processing time, good markdown quality

### DOCX Documents

#### `docx/with_tables/`
Microsoft Word documents containing various table formats.
- **Characteristics**: Complex tables, merged cells, nested structures
- **Expected Behavior**: Table preservation in markdown format

#### `docx/with_images/`
Microsoft Word documents containing embedded images.
- **Characteristics**: Inline images, image captions, mixed content
- **Expected Behavior**: Image placeholder insertion in markdown

### PPTX Documents

#### `pptx/complex_layouts/`
PowerPoint presentations with complex slide layouts.
- **Characteristics**: Multi-column layouts, text boxes, shapes
- **Expected Behavior**: Layout simplification, text extraction, hierarchy preservation

### XLSX Documents

#### `xlsx/multiple_sheets/`
Excel spreadsheets with multiple worksheets and formulas.
- **Characteristics**: Multiple sheets, formulas, data tables
- **Expected Behavior**: Sheet separation, table conversion to markdown

### Edge Cases

#### `edge_cases/password_protected/`
Password-protected documents (various formats).
- **Characteristics**: Encrypted files requiring passwords
- **Expected Behavior**: Graceful failure with `PASSWORD_PROTECTED` error

#### `edge_cases/corrupted/`
Corrupted or malformed document files.
- **Characteristics**: Invalid file structure, incomplete data
- **Expected Behavior**: Graceful failure with `CORRUPTED_FILE` error

#### `edge_cases/size_limits/`
Files at or exceeding size limits.
- **Characteristics**: 9.9MB (under limit), 10.1MB (over limit), 15MB (well over)
- **Expected Behavior**: Files >10MB should fail with `FILE_TOO_LARGE` error

#### `edge_cases/special_characters/`
Files with special characters in filenames.
- **Characteristics**: Unicode characters, spaces, symbols
- **Expected Behavior**: Proper filename sanitization and handling

### Multilingual Documents

#### `multilingual/`
Documents in various non-English languages.
- **Characteristics**: Chinese, Arabic, Spanish, mixed-language content
- **Expected Behavior**: Proper text extraction, encoding handling

## Test Document Specifications

### File Naming Convention
Files should be named descriptively to indicate their characteristics:
- `{type}_{characteristic}_{number}.{ext}`
- Example: `pdf_clean_digital_tables_01.pdf`
- Example: `docx_with_tables_complex_01.docx`

### Documented Characteristics
Each test file should have its characteristics documented in a companion `.info.json` file:

```json
{
  "filename": "pdf_clean_digital_01.pdf",
  "type": "pdf",
  "category": "clean_digital",
  "size_bytes": 245678,
  "page_count": 5,
  "features": ["tables", "headings", "bullet_lists"],
  "expected_processing_time_seconds": 15,
  "expected_quality_score": 0.95,
  "notes": "Standard business document with tables and sections"
}
```

## Acquiring Test Documents

### Sources for Test Documents
1. **Open-source document repositories**: Internet Archive, Project Gutenberg
2. **Generated test documents**: Create using LibreOffice, Google Docs, Microsoft Office
3. **Real workshop documents**: Anonymized versions of actual documents
4. **Synthetic test cases**: Programmatically generated edge case documents

### Document Requirements
- **Diversity**: Cover all supported file types (PDF, DOCX, PPTX, XLSX)
- **Complexity Levels**: Simple, moderate, complex for each type
- **Size Range**: Small (<100KB), medium (1-5MB), large (5-10MB)
- **Language Coverage**: English, non-English, mixed-language
- **Quality Levels**: High-quality digital, scanned, degraded

## Test Coverage Goals

- **Document Types**: 100% coverage of supported formats
- **Edge Cases**: All known failure scenarios tested
- **Quality Levels**: Low, medium, high quality samples for each type
- **Size Distribution**: Representative file sizes across the spectrum
- **Language Coverage**: At least 3 non-English languages

## Usage in Tests

These fixtures are used by:
- `backend/tests/integration/test_diverse_documents.py` - Main document type testing
- `backend/tests/integration/test_edge_cases.py` - Edge case validation
- `backend/tests/performance/test_benchmarks.py` - Performance benchmarking

## Maintenance

- **Regular Updates**: Add new edge cases as discovered
- **Version Control**: Track test documents in Git (within size limits)
- **External Storage**: Large test documents stored externally with download scripts
- **Documentation**: Keep this README updated with new test categories
