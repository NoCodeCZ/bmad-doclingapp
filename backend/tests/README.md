# Integration Test Suite

## Overview

Comprehensive integration test suite for the Docling App document processing system, covering end-to-end workflows, error scenarios, performance benchmarking, and storage failures.

## Test Structure

### Integration Tests (`backend/tests/test_integration/`)

1. **test_complete_workflow.py** - End-to-end document processing workflows
   - PDF upload → process → download
   - DOCX upload → process → download
   - PPTX upload → process → download
   - XLSX upload → process → download
   - File integrity verification
   - Processing time measurement

2. **test_processing_options_integration.py** - Processing options validation
   - Fast vs Quality mode performance comparison
   - OCR functionality testing
   - All processing option combinations (Fast/Quality × OCR on/off)
   - Output quality differences between modes
   - Processing time documentation

3. **test_error_scenarios.py** - Error scenario handling
   - Oversized file rejection (11MB+)
   - Unsupported format rejection (.txt, .jpg, etc.)
   - Corrupted file handling
   - User-friendly error messages validation
   - Error state cleanup and recovery
   - Multiple validation errors
   - Empty file rejection
   - Special characters in filenames

4. **test_timeout_scenarios.py** - Timeout detection and handling
   - Processing timeout detection (5-minute limit)
   - Timeout error message generation
   - System cleanup after timeout
   - Retry functionality after timeout
   - Timeout with different processing modes
   - Timeout at different processing stages
   - Concurrent timeout handling

5. **test_storage_failures.py** - Storage failure scenarios
   - Upload storage failure handling
   - Download storage failure handling
   - Supabase connection error handling
   - Storage retry logic
   - Partial storage failure handling
   - Database query failure
   - Storage timeout handling
   - Storage quota exceeded
   - Intermittent storage failures
   - Graceful degradation and user feedback
   - Storage recovery after failure

6. **test_performance_benchmarks.py** - Performance benchmarking
   - Processing time percentiles (p50, p95, p99)
   - Benchmark by file size (small, medium, large)
   - Concurrent processing performance
   - Performance by file type
   - Performance regression detection
   - Memory usage estimation

## Test Fixtures

### Integration Test Fixtures (`backend/tests/fixtures/integration/`)

- **simple_document.pdf** - Basic PDF for testing
- **complex_document.pdf** - Complex PDF with tables (to be created)
- **scanned_document.pdf** - Scanned PDF for OCR testing (to be created)
- **oversized_document.pdf** - 11MB+ file for size limit testing
- **corrupted_document.pdf** - Intentionally corrupted PDF
- **unsupported_file.txt** - Unsupported format for testing

### Fixture Management

The `TestFixtureManager` class provides:
- Centralized fixture path management
- Dynamic fixture creation for special cases
- Fixture existence validation

## Configuration

### Test Configuration (`conftest.py`)

```python
class IntegrationTestConfig:
    TEST_DATABASE_URL = "postgresql://test_user:test_pass@localhost:5432/test_docling"
    MOCK_SUPABASE = True
    MOCK_DOCLING = True
    TEST_FIXTURES_DIR = "backend/tests/fixtures/integration/"
    MAX_PROCESSING_TIME_FAST = 60  # seconds
    MAX_PROCESSING_TIME_QUALITY = 180  # seconds
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    MIN_SUCCESS_RATE = 0.95  # 95%
    MAX_ERROR_RATE = 0.05  # 5%
```

### Pytest Markers

- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.staging` - Staging environment tests
- `@pytest.mark.performance` - Performance benchmark tests
- `@pytest.mark.error_scenario` - Error scenario tests

## Running Tests

### Install Test Dependencies

```bash
pip install -r backend/requirements-test.txt
```

### Run All Integration Tests

```bash
pytest backend/tests/test_integration/ -v
```

### Run Specific Test Suite

```bash
# Complete workflow tests
pytest backend/tests/test_integration/test_complete_workflow.py -v

# Error scenario tests
pytest backend/tests/test_integration/test_error_scenarios.py -v

# Performance benchmarks
pytest backend/tests/test_integration/test_performance_benchmarks.py -v
```

### Run with Coverage

```bash
pytest backend/tests/test_integration/ --cov=app --cov-report=html
```

### Run Performance Tests Only

```bash
pytest backend/tests/test_integration/ -m performance -v
```

### Run Error Scenario Tests Only

```bash
pytest backend/tests/test_integration/ -m error_scenario -v
```

## Test Utilities

### WorkflowTestHelper

Helper class for testing complete workflows:

- `measure_processing_time()` - Measure document processing time
- `test_complete_workflow()` - Test complete upload → process → download

### PerformanceMetrics

Track and analyze performance metrics:

- `record_processing()` - Record processing results
- `calculate_percentiles()` - Calculate p50, p95, p99
- `get_success_rate()` - Calculate success rate
- `get_metrics_by_file_type()` - Group metrics by file type
- `get_metrics_by_mode()` - Group metrics by processing mode

## Performance Thresholds

### Processing Time Limits

- **Fast Mode**: Maximum 60 seconds
- **Quality Mode**: Maximum 180 seconds
- **OCR Additional Overhead**: Up to 60 seconds

### Success Rate Requirements

- **Minimum Success Rate**: 95%
- **Maximum Error Rate**: 5%

### File Size Limits

- **Maximum File Size**: 10MB
- **Test Oversized**: 11MB (should be rejected)

## Expected Test Results

### Success Criteria

- ✅ All file types process successfully (PDF, DOCX, PPTX, XLSX)
- ✅ Fast mode completes faster than Quality mode
- ✅ OCR mode extracts text from scanned documents
- ✅ Oversized files rejected with user-friendly error
- ✅ Unsupported formats rejected with clear message
- ✅ Corrupted files fail gracefully with error message
- ✅ Timeout detected after 5 minutes with proper error
- ✅ Storage failures handled gracefully
- ✅ 95%+ success rate across all scenarios
- ✅ Processing time percentiles within thresholds

### Performance Benchmarks

Based on test execution, expected percentiles:

- **p50 (median)**: < 60 seconds
- **p95**: < 120 seconds
- **p99**: < 180 seconds

## CI/CD Integration

### GitHub Actions Workflow (Placeholder)

```yaml
name: Integration Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: |
          pip install -r backend/requirements.txt
          pip install -r backend/requirements-test.txt
      - name: Run integration tests
        run: |
          pytest backend/tests/test_integration/ -v --tb=short
```

## Known Issues & Limitations

1. **Dependency Conflicts**: Realtime package version conflicts may occur. Ensure compatible versions.
2. **Mock Services**: Tests use mocked Supabase and Docling services for isolation.
3. **Real Document Testing**: Staging environment tests require actual workshop documents.
4. **Cross-Browser Tests**: Frontend integration tests for cross-browser compatibility pending.

## Next Steps

1. Create actual complex document fixtures (PDF with tables, multi-slide PPTX, large XLSX)
2. Implement staging environment E2E tests with real workshop documents
3. Add cross-browser compatibility tests for frontend
4. Set up CI/CD pipeline for automated test execution
5. Implement test results documentation and reporting
6. Create performance regression detection baselines

## Documentation

- Test Architecture: `docs/architecture.md#Testing-Strategy`
- QA Review: `docs/qa/story-2.6-integration-testing-error-scenario-validation-qa-review.md`
- Quality Gate: `docs/qa/gates/2.6.integration-testing-error-scenario-validation-gate.md`
