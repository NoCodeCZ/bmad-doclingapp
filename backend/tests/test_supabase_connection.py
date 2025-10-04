#!/usr/bin/env python3
"""
Supabase Connection Test Script
Run this to verify Supabase configuration and smoke test the complete workflow.
"""

import os
import sys
import asyncio
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.supabase_service import supabase_service
from app.core.config import settings


async def test_database_connection():
    """Test database connectivity."""
    print("=" * 60)
    print("TEST 1: Database Connection")
    print("=" * 60)
    
    try:
        if supabase_service.client is None:
            print("❌ FAILED: Supabase client not initialized")
            print(f"   SUPABASE_URL: {settings.SUPABASE_URL}")
            print(f"   SUPABASE_KEY: {settings.SUPABASE_KEY[:20]}..." if settings.SUPABASE_KEY else "   SUPABASE_KEY: Not set")
            return False
        
        # Test database query
        result = supabase_service.client.table('documents').select('id').limit(1).execute()
        print("✅ PASSED: Database connected successfully")
        print(f"   Query executed successfully")
        return True
        
    except Exception as e:
        print(f"❌ FAILED: Database connection error")
        print(f"   Error: {str(e)}")
        return False


async def test_storage_connection():
    """Test storage connectivity."""
    print("\n" + "=" * 60)
    print("TEST 2: Storage Connection")
    print("=" * 60)
    
    try:
        if supabase_service.client is None:
            print("❌ FAILED: Supabase client not initialized")
            return False
        
        # Test storage by listing buckets
        buckets = supabase_service.client.storage.list_buckets()
        print("✅ PASSED: Storage connected successfully")
        print(f"   Found {len(buckets)} buckets")
        
        # Check for required buckets
        bucket_names = [b.name for b in buckets]
        if 'uploads' in bucket_names:
            print("   ✓ 'uploads' bucket exists")
        else:
            print("   ⚠️  'uploads' bucket missing")
            
        if 'processed' in bucket_names:
            print("   ✓ 'processed' bucket exists")
        else:
            print("   ⚠️  'processed' bucket missing")
        
        return True
        
    except Exception as e:
        print(f"❌ FAILED: Storage connection error")
        print(f"   Error: {str(e)}")
        return False


async def test_create_document():
    """Test creating a document record."""
    print("\n" + "=" * 60)
    print("TEST 3: Create Document Record")
    print("=" * 60)
    
    try:
        # Create a test document record
        doc_id = await supabase_service.create_document_record(
            filename="test.pdf",
            processing_options={"ocr_enabled": False, "processing_mode": "fast"}
        )
        print("✅ PASSED: Document record created successfully")
        print(f"   Document ID: {doc_id}")
        
        # Cleanup: delete the test record
        try:
            supabase_service.client.table('documents').delete().eq('id', doc_id).execute()
            print("   ✓ Test record cleaned up")
        except:
            pass
            
        return True
        
    except Exception as e:
        print(f"❌ FAILED: Could not create document record")
        print(f"   Error: {str(e)}")
        return False


async def test_storage_upload():
    """Test file upload to storage."""
    print("\n" + "=" * 60)
    print("TEST 4: Storage Upload")
    print("=" * 60)
    
    try:
        # Create a test file
        test_content = b"This is a test file for smoke testing"
        test_filename = "test-smoke-test.txt"
        
        # Upload to storage
        await supabase_service.upload_file(
            bucket="uploads",
            file_path=test_filename,
            file_content=test_content,
            content_type="text/plain"
        )
        print("✅ PASSED: File uploaded successfully")
        print(f"   File: {test_filename}")
        
        # Cleanup: delete the test file
        try:
            await supabase_service.delete_file("uploads", test_filename)
            print("   ✓ Test file cleaned up")
        except:
            pass
            
        return True
        
    except Exception as e:
        print(f"❌ FAILED: Could not upload file")
        print(f"   Error: {str(e)}")
        return False


async def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("SUPABASE CONFIGURATION & SMOKE TEST")
    print("=" * 60)
    print(f"\nConfiguration:")
    print(f"  SUPABASE_URL: {settings.SUPABASE_URL}")
    print(f"  SUPABASE_KEY: {settings.SUPABASE_KEY[:20]}..." if settings.SUPABASE_KEY else "  SUPABASE_KEY: Not set")
    print()
    
    results = []
    
    # Run tests
    results.append(await test_database_connection())
    results.append(await test_storage_connection())
    results.append(await test_create_document())
    results.append(await test_storage_upload())
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"✅ ALL TESTS PASSED ({passed}/{total})")
        print("\n🎉 Supabase is configured correctly!")
        print("\nNext steps:")
        print("  1. Test the health endpoint: curl http://localhost:8000/api/health")
        print("  2. Upload a test PDF through the frontend: http://localhost:3000")
        print("  3. Verify end-to-end workflow completion")
        return 0
    else:
        print(f"❌ SOME TESTS FAILED ({passed}/{total} passed)")
        print("\n⚠️  Please check the errors above and:")
        print("  1. Verify Supabase credentials in backend/.env")
        print("  2. Ensure migration has been run in Supabase SQL Editor")
        print("  3. Check that storage buckets exist")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)