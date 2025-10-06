# Workshop Document Processor - Known Limitations

**Document Version:** 1.0
**Last Updated:** October 6, 2025
**Target Workshop Date:** October 17, 2025

## Overview

This document outlines the known limitations of the Workshop Document Processor to set appropriate expectations for workshop attendees and facilitators. Understanding these limitations will help users achieve the best results when processing documents for RAG usage in Open WebUI.

---

## File Type Limitations

### Supported Formats

| Format | Support Level | Notes |
|--------|--------------|-------|
| PDF | ✅ Full Support | Both digital and scanned PDFs |
| DOCX | ✅ Full Support | Microsoft Word documents |
| PPTX | ✅ Full Support | PowerPoint presentations |
| XLSX | ✅ Full Support | Excel spreadsheets |

### Unsupported Formats

| Format | Status | Workaround |
|--------|--------|------------|
| DOC (old Word) | ❌ Not Supported | Convert to DOCX using Microsoft Word or LibreOffice |
| PPT (old PowerPoint) | ❌ Not Supported | Convert to PPTX using PowerPoint |
| XLS (old Excel) | ❌ Not Supported | Convert to XLSX using Excel |
| Images (PNG, JPG) | ❌ Not Supported | Embed in PDF or DOCX first |
| HTML | ❌ Not Supported | Convert to PDF using browser print function |
| TXT/MD | ⚠️ Limited | Processed as-is, no structure extraction |

---

## File Size Limitations

### Maximum File Size

- **Hard Limit:** 10 MB
- **Recommended Maximum:** 8 MB for optimal performance

### Size-Related Issues

| File Size | Expected Behavior | Processing Time |
|-----------|------------------|-----------------|
| < 1 MB | Fast, reliable processing | < 30 seconds |
| 1-5 MB | Good performance | 30 seconds - 2 minutes |
| 5-10 MB | Slower processing | 2-5 minutes |
| > 10 MB | **Rejected** with `FILE_TOO_LARGE` error | N/A |

**Workaround for Large Files:**
- Split large documents into smaller sections
- Compress PDF files using Adobe Acrobat or similar tools
- Remove unnecessary images or compress image quality

---

## Content Processing Limitations

### Document Features with Quality Degradation

| Feature | Support Level | Quality Notes |
|---------|--------------|---------------|
| **Simple Tables** | ✅ Excellent | Well-preserved in markdown format |
| **Complex Tables** | ⚠️ Partial | Merged cells may lose structure |
| **Nested Tables** | ⚠️ Partial | Often flattened or simplified |
| **Images** | ⚠️ Placeholder Only | Replaced with `![image]` placeholder text |
| **Charts & Graphs** | ❌ Not Preserved | Converted to placeholder or lost |
| **Embedded Videos** | ❌ Not Supported | Completely removed from output |
| **Hyperlinks** | ⚠️ Partial | Link text preserved, URLs may be lost |
| **Comments & Annotations** | ❌ Not Preserved | Removed during processing |
| **Headers & Footers** | ⚠️ Partial | May be included as regular text |
| **Equations** | ⚠️ Limited | Simple equations preserved, complex LaTeX may fail |

### Text Extraction Limitations

| Document Type | Limitation | Impact |
|--------------|------------|--------|
| **Scanned PDFs (Low Quality)** | OCR accuracy < 90% | Spelling errors, missing text |
| **Scanned PDFs (High Quality)** | OCR accuracy 95-99% | Minor errors possible |
| **Multi-Column Layouts** | Column order may be incorrect | Text flow disruption |
| **Text Boxes (PPTX)** | Reading order unpredictable | Content may appear out of order |
| **Handwritten Text** | Very poor OCR accuracy | Not recommended |
| **Non-English Languages** | Variable OCR accuracy | Best results with Latin scripts |

---

## Processing Mode Limitations

### Fast Mode

- **Best For:** Simple documents, digital PDFs, quick testing
- **Limitations:**
  - Lower OCR accuracy for scanned documents
  - Simplified table structure
  - Reduced image description quality
  - May miss subtle formatting

### Quality Mode

- **Best For:** Complex documents, scanned PDFs, production use
- **Limitations:**
  - Longer processing time (2-5x slower)
  - Still cannot preserve all formatting
  - Charts and complex graphics still simplified
  - File size limits still apply

---

## Language and Encoding Limitations

### Supported Languages (OCR)

| Language | Support Level | Notes |
|----------|--------------|-------|
| English | ✅ Excellent | 95-99% accuracy |
| Spanish | ✅ Excellent | 95-99% accuracy |
| French | ✅ Excellent | 95-99% accuracy |
| German | ✅ Excellent | 95-99% accuracy |
| Chinese (Simplified) | ⚠️ Good | 85-95% accuracy |
| Arabic | ⚠️ Moderate | 75-90% accuracy, RTL may have issues |
| Japanese | ⚠️ Moderate | 75-90% accuracy |
| Mixed Languages | ⚠️ Variable | Accuracy depends on primary language |

### Character Encoding

- **UTF-8:** Fully supported
- **Special Characters:** Generally preserved
- **Emoji:** May be lost or converted to text descriptions
- **Mathematical Symbols:** Partial support

---

## Security and Privacy Limitations

### Password-Protected Files

| Protection Type | Behavior | Error Code |
|----------------|----------|------------|
| Password-Protected PDF | ❌ Rejected | `PASSWORD_PROTECTED` |
| Password-Protected DOCX | ❌ Rejected | `PASSWORD_PROTECTED` |
| Encrypted Documents | ❌ Rejected | `CORRUPTED_FILE` or `PASSWORD_PROTECTED` |

**Workaround:** Remove password protection before uploading

### Data Retention

- **Upload Storage:** Files stored in Supabase private buckets
- **Processing Results:** Markdown output stored indefinitely (MVP)
- **User Responsibility:** Delete sensitive documents after download
- **No Authentication:** Anyone with the URL can access the tool

---

## Performance Limitations

### Concurrent Processing

| Load Level | Expected Behavior | Notes |
|------------|------------------|-------|
| 1-10 users | Excellent performance | < 1 minute wait |
| 10-20 users | Good performance | 1-3 minute wait |
| 20-30 users | Acceptable performance | 2-5 minute wait |
| > 30 users | ⚠️ Degraded | Queueing may occur |

### Processing Timeouts

- **Maximum Processing Time:** 5 minutes
- **Timeout Behavior:** Returns `PROCESSING_TIMEOUT` error
- **Retry Policy:** Manual retry required

### Network Limitations

- **Upload Speed:** Depends on user's internet connection
- **Download Speed:** Limited by DigitalOcean CDN bandwidth
- **Connection Stability:** Interruptions will fail the upload

---

## Known Bugs and Issues

### Critical Issues (Must Know)

1. **Very Large Tables (> 100 rows)**
   - **Issue:** May cause processing timeouts
   - **Workaround:** Split document into smaller sections
   - **Status:** Known limitation, no fix planned for MVP

2. **Complex Nested Structures**
   - **Issue:** Deeply nested lists or tables may be flattened
   - **Workaround:** Simplify document structure before upload
   - **Status:** Docling limitation, no workaround

3. **Image-Heavy Documents**
   - **Issue:** Documents with many images process slowly
   - **Workaround:** Reduce image count or quality
   - **Status:** Performance limitation

### Non-Critical Issues (Nice to Know)

1. **Filename Special Characters**
   - **Issue:** Some special characters in filenames are sanitized
   - **Impact:** Downloaded file may have slightly different name
   - **Status:** Working as intended

2. **Mobile Upload on Safari**
   - **Issue:** File picker may not show all file types
   - **Workaround:** Use Chrome or Firefox on mobile
   - **Status:** Browser-specific behavior

3. **Very Long Filenames**
   - **Issue:** Filenames > 200 characters may be truncated
   - **Impact:** Minor, download filename shortened
   - **Status:** Low priority

---

## Acceptable Quality Degradation Scenarios

### When to Accept Lower Quality

1. **Quick Workshop Demos**
   - Fast mode is acceptable for time-constrained demonstrations
   - Minor formatting issues won't impact RAG functionality significantly

2. **Text-Heavy Documents**
   - Simple documents with mostly text will have excellent results
   - Table and image limitations have minimal impact

3. **Scanned Documents (High Quality)**
   - OCR accuracy of 95%+ is acceptable for most RAG use cases
   - Minor typos can be manually corrected post-processing

### When Quality is Critical

1. **Technical Documentation with Complex Tables**
   - **Recommendation:** Use Quality mode + manual verification
   - **Alternative:** Consider restructuring tables for better preservation

2. **Multi-Language Documents**
   - **Recommendation:** Test with sample page first
   - **Alternative:** Process each language section separately

3. **Documents with Critical Data Accuracy**
   - **Recommendation:** Manual review of markdown output required
   - **Alternative:** Use source documents directly if 100% accuracy needed

---

## Workshop-Specific Recommendations

### For Workshop Facilitators

1. **Pre-Workshop Testing**
   - Test with representative sample documents
   - Identify any attendee documents that may have issues
   - Prepare alternative documents if needed

2. **Setting Expectations**
   - Emphasize text extraction capabilities
   - Acknowledge formatting limitations upfront
   - Highlight that output is optimized for RAG, not visual fidelity

3. **Troubleshooting Ready**
   - Keep list of common issues and workarounds handy
   - Have sample documents ready for demos
   - Know when to suggest document restructuring

### For Workshop Attendees

1. **Document Preparation**
   - Use digital documents when possible (not scans)
   - Keep file sizes under 5MB for best performance
   - Simplify complex layouts before processing

2. **Processing Mode Selection**
   - Use Fast mode for initial testing
   - Switch to Quality mode for final processing
   - Enable OCR only for scanned documents

3. **Quality Validation**
   - Always review markdown output before using in Open WebUI
   - Check that critical tables and data are preserved
   - Manually correct any OCR errors if needed

---

## Future Enhancements (Post-Workshop)

### Planned Improvements

1. **Batch Processing**
   - Process multiple documents simultaneously
   - Status: Planned for future release

2. **Enhanced Table Preservation**
   - Better handling of merged cells and complex tables
   - Status: Dependent on Docling updates

3. **Video/Audio Transcription**
   - Extract and transcribe embedded media
   - Status: Out of scope for MVP

4. **Authentication & User Accounts**
   - Secure document storage and history
   - Status: Planned for production version

### Community Feedback

- Users can report issues and limitations discovered during workshop
- Feedback will inform future development priorities
- Known limitations will be updated based on real-world usage

---

## Limitation Matrix for Quick Reference

| Category | Supported | Limited | Not Supported |
|----------|-----------|---------|---------------|
| **File Types** | PDF, DOCX, PPTX, XLSX | TXT, MD | DOC, PPT, XLS, Images |
| **File Size** | < 5 MB optimal | 5-10 MB slower | > 10 MB rejected |
| **Tables** | Simple tables | Complex/nested | Charts, graphs |
| **Images** | Placeholder | - | Actual images |
| **Text** | Digital text | Scanned (OCR) | Handwritten |
| **Languages** | English, major European | CJK languages | Rare languages |
| **Security** | Public documents | - | Password-protected |

---

## Contact for Issues

- **During Workshop:** Ask workshop facilitator
- **Technical Issues:** Check troubleshooting guide in Instructions page
- **Post-Workshop Feedback:** [Contact information TBD]

---

*This document will be updated based on testing results and workshop feedback.*
