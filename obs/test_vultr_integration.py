#!/usr/bin/env python3
"""
Test script for Vultr integration

This script tests the Vultr upload service and integration with the recording system.
"""

import asyncio
import sys
import time
from pathlib import Path
from vultr_service import vultr_service
from config import config
from recording_manager import RecordingManager

async def test_vultr_integration():
    """Test Vultr integration functionality"""
    print("🧪 Testing Vultr Integration")
    print("=" * 50)
    
    # Test 1: Configuration
    print("\n1. Testing Vultr Configuration")
    print("-" * 30)
    
    vultr_config = config.get_vultr_config()
    print(f"API URL: {vultr_config['api_url']}")
    print(f"Upload Endpoint: {vultr_config['upload_endpoint']}")
    print(f"Auto Upload: {vultr_config['auto_upload']}")
    
    if vultr_service.is_configured():
        print("✅ Vultr service is configured")
    else:
        print("❌ Vultr service is not configured")
        return False
    
    # Test 2: Connection
    print("\n2. Testing Vultr Connection")
    print("-" * 30)
    
    connection_test = vultr_service.test_connection()
    if connection_test['success']:
        print("✅ Connection to Vultr server successful")
        if connection_test.get('server_info'):
            print(f"Server Info: {connection_test['server_info']}")
    else:
        print(f"❌ Connection failed: {connection_test['error']}")
        print("⚠️ Continuing with other tests...")
    
    # Test 3: Recording Manager Integration
    print("\n3. Testing Recording Manager Integration")
    print("-" * 30)
    
    recording_manager = RecordingManager()
    
    try:
        # Initialize recording manager
        success = await recording_manager.initialize()
        if success:
            print("✅ Recording Manager initialized successfully")
        else:
            print("❌ Recording Manager initialization failed")
            return False
        
        # Check system status
        status = recording_manager.get_system_status()
        print(f"OBS Connected: {'✅' if status['obs_connected'] else '❌'}")
        print(f"YouTube Authenticated: {'✅' if status['youtube_authenticated'] else '❌'}")
        
        # Test 4: Mock Upload (if we have test files)
        print("\n4. Testing File Upload (Mock)")
        print("-" * 30)
        
        # Look for existing recordings to test with
        recordings_path = config.get_recordings_path()
        test_files = []
        
        if recordings_path.exists():
            for session_dir in recordings_path.iterdir():
                if session_dir.is_dir():
                    video_files = [f for f in session_dir.iterdir() 
                                 if f.is_file() and f.suffix.lower() in ['.mkv', '.mp4', '.avi', '.mov']]
                    if video_files:
                        test_files.extend(video_files[:1])  # Take first video from each session
                        break  # Only test with one file
        
        if test_files:
            test_file = test_files[0]
            print(f"Testing upload with: {test_file.name}")
            print(f"File size: {test_file.stat().st_size / (1024*1024):.1f} MB")
            
            # Only test upload if connection was successful
            if connection_test['success']:
                print("🚀 Starting upload test...")
                
                upload_result = vultr_service.upload_file(
                    test_file,
                    session_name="test_integration",
                    auto_process=False  # Don't auto-process for test
                )
                
                if upload_result['success']:
                    print(f"✅ Upload successful!")
                    print(f"Task ID: {upload_result['task_id']}")
                    print(f"Upload Time: {upload_result['upload_time']}")
                    
                    # Test status check
                    print("\n5. Testing Status Check")
                    print("-" * 30)
                    
                    time.sleep(2)  # Wait a moment
                    status_result = vultr_service.get_upload_status(upload_result['task_id'])
                    
                    if status_result['success']:
                        print("✅ Status check successful")
                        print(f"Status: {status_result['status']}")
                    else:
                        print(f"❌ Status check failed: {status_result['error']}")
                        
                else:
                    print(f"❌ Upload failed: {upload_result['error']}")
            else:
                print("⚠️ Skipping upload test due to connection failure")
        else:
            print("⚠️ No test files found, skipping upload test")
            print("   Create a recording first to test upload functionality")
        
        # Test 5: List Uploads
        print("\n6. Testing List Uploads")
        print("-" * 30)
        
        if connection_test['success']:
            list_result = vultr_service.list_uploads(limit=5)
            
            if list_result['success']:
                uploads = list_result['uploads']
                print(f"✅ Found {len(uploads)} recent uploads")
                for i, upload in enumerate(uploads[:3], 1):
                    print(f"  {i}. {upload.get('filename', 'Unknown')} - {upload.get('status', 'Unknown')}")
            else:
                print(f"❌ List uploads failed: {list_result['error']}")
        else:
            print("⚠️ Skipping list uploads test due to connection failure")
        
        # Test 6: Auto-upload Configuration
        print("\n7. Testing Auto-upload Configuration")
        print("-" * 30)
        
        if vultr_config['auto_upload']:
            print("✅ Auto-upload is ENABLED")
            print("   Recordings will be automatically uploaded to Vultr after stopping")
        else:
            print("⚠️ Auto-upload is DISABLED")
            print("   Enable with VULTR_AUTO_UPLOAD=true in .env file")
        
        print("\n" + "=" * 50)
        print("🎉 Vultr Integration Test Completed!")
        print("=" * 50)
        
        # Summary
        print("\n📋 Summary:")
        print(f"✅ Configuration: {'OK' if vultr_service.is_configured() else 'FAILED'}")
        print(f"✅ Connection: {'OK' if connection_test['success'] else 'FAILED'}")
        print(f"✅ Recording Manager: OK")
        print(f"✅ Auto-upload: {'ENABLED' if vultr_config['auto_upload'] else 'DISABLED'}")
        
        if connection_test['success']:
            print("\n🚀 Ready to use Vultr integration!")
            print("   • Start a recording with: python main.py record")
            print("   • Upload manually via API: POST /api/vultr/upload")
            print("   • Check status via API: GET /api/vultr/status")
        else:
            print("\n⚠️ Connection issues detected:")
            print("   • Check Vultr server is running")
            print("   • Verify VULTR_API_URL in .env file")
            print("   • Check network connectivity")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False
    finally:
        await recording_manager.cleanup()

def main():
    """Main entry point"""
    try:
        result = asyncio.run(test_vultr_integration())
        return 0 if result else 1
    except KeyboardInterrupt:
        print("\n\n⏹️ Test cancelled by user")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
