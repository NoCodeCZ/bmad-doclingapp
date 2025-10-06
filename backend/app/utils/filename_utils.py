"""
Filename cleaning utilities for safe, cross-platform filename handling.

Implements AC3: Filename cleaning with extension replacement and special character removal.
Security: Prevents path traversal attacks and ensures cross-platform compatibility.
"""

import re
import os
from typing import Optional


def clean_filename(original_filename: str, replacement_ext: str = ".md") -> str:
    """
    Clean filename by replacing extension and removing special characters.

    Security measures:
    - Removes path traversal characters (../, /, \\)
    - Removes OS-specific problematic characters
    - Prevents null bytes and control characters
    - Ensures reasonable filename length

    Args:
        original_filename: Original uploaded filename
        replacement_ext: New file extension (default: .md)

    Returns:
        Cleaned filename with replacement extension

    Examples:
        >>> clean_filename("My Document.pdf")
        'My_Document.md'

        >>> clean_filename("report<2024>.docx")
        'report_2024.md'

        >>> clean_filename("../../../etc/passwd.pdf")
        'etc_passwd.md'
    """
    if not original_filename or not isinstance(original_filename, str):
        return f"document{replacement_ext}"

    # Security: Remove any path components to prevent path traversal
    # This handles both forward slashes and backslashes
    filename_only = os.path.basename(original_filename)

    # Remove file extension (handles .pdf, .docx, .pptx, .xlsx, etc.)
    name_without_ext = os.path.splitext(filename_only)[0]

    if not name_without_ext:
        return f"document{replacement_ext}"

    # Security: Remove null bytes and control characters
    cleaned = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', name_without_ext)

    # Security: Remove problematic characters for cross-platform compatibility
    # Windows reserved characters: < > : " / \ | ? *
    # Also remove additional problematic characters
    cleaned = re.sub(r'[<>:"/\\|?*\x00]', '', cleaned)

    # Replace spaces with underscores for better URL compatibility
    cleaned = cleaned.replace(' ', '_')

    # Remove multiple consecutive underscores
    cleaned = re.sub(r'_+', '_', cleaned)

    # Remove leading/trailing underscores and dots
    cleaned = cleaned.strip('_.')

    # Security: Limit filename length (max 200 chars before extension)
    # This prevents filesystem issues and ensures compatibility
    if len(cleaned) > 200:
        cleaned = cleaned[:200].rstrip('_.')

    # If cleaning resulted in empty string, use default
    if not cleaned:
        return f"document{replacement_ext}"

    # Ensure extension starts with a dot
    if replacement_ext and not replacement_ext.startswith('.'):
        replacement_ext = f".{replacement_ext}"

    return f"{cleaned}{replacement_ext}"


def sanitize_path_component(path_component: str) -> str:
    """
    Sanitize a path component to prevent directory traversal attacks.

    Args:
        path_component: Path component to sanitize

    Returns:
        Sanitized path component safe for filesystem operations

    Examples:
        >>> sanitize_path_component("../../../etc/passwd")
        'etc_passwd'

        >>> sanitize_path_component("normal_file.txt")
        'normal_file.txt'
    """
    if not path_component or not isinstance(path_component, str):
        return "file"

    # Remove any path separators to prevent directory traversal
    sanitized = path_component.replace('..', '').replace('/', '_').replace('\\', '_')

    # Remove null bytes
    sanitized = sanitized.replace('\x00', '')

    # Remove leading/trailing whitespace and dots
    sanitized = sanitized.strip('. ')

    return sanitized if sanitized else "file"


def validate_filename(filename: str, max_length: int = 255) -> bool:
    """
    Validate that a filename is safe and within reasonable constraints.

    Args:
        filename: Filename to validate
        max_length: Maximum allowed filename length (default: 255)

    Returns:
        True if filename is valid, False otherwise

    Examples:
        >>> validate_filename("document.md")
        True

        >>> validate_filename("a" * 300 + ".md")
        False
    """
    if not filename or not isinstance(filename, str):
        return False

    # Check length
    if len(filename) > max_length:
        return False

    # Check for null bytes
    if '\x00' in filename:
        return False

    # Check for path traversal attempts
    if '..' in filename or '/' in filename or '\\' in filename:
        return False

    # Check for reserved Windows filenames
    reserved_names = {
        'CON', 'PRN', 'AUX', 'NUL',
        'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
        'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'
    }
    name_without_ext = os.path.splitext(filename)[0].upper()
    if name_without_ext in reserved_names:
        return False

    return True


def get_safe_filename(filename: str, fallback: str = "document.md") -> str:
    """
    Get a safe filename, falling back to a default if validation fails.

    This is a convenience function that combines cleaning and validation.

    Args:
        filename: Original filename
        fallback: Fallback filename if validation fails

    Returns:
        Safe filename or fallback

    Examples:
        >>> get_safe_filename("My Report.pdf")
        'My_Report.md'

        >>> get_safe_filename("../../../etc/passwd")
        'etc_passwd.md'
    """
    cleaned = clean_filename(filename)

    if validate_filename(cleaned):
        return cleaned

    return fallback
