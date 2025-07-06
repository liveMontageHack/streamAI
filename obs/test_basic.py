#!/usr/bin/env python3
"""
Basic test script to verify core functionality without external dependencies
"""

import sys
import os
from pathlib import Path

def test_imports():
    """Test if all modules can be imported"""
    print("Testing module imports...")
    
    try:
        import config
        print("✅ config module imported successfully")
    except Exception as e:
        print(f"❌ Failed to import config: {e}")
        return False
    
    try:
        from obs_controller import OBSController
        print("✅ obs_controller module imported successfully")
    except Exception as e:
        print(f"❌ Failed to import obs_controller: {e}")
        return False
    
    try:
        from youtube_api import YouTubeAPI
        print("✅ youtube_api module imported successfully")
    except Exception as e:
        print(f"❌ Failed to import youtube_api: {e}")
        return False
    
    try:
        from recording_manager import RecordingManager
        print("✅ recording_manager module imported successfully")
    except Exception as e:
        print(f"❌ Failed to import recording_manager: {e}")
        return False
    
    return True

def test_config():
    """Test configuration loading"""
    print("\nTesting configuration...")
    
    try:
        from config import config
        print(f"✅ Config loaded")
        print(f"   Recordings path: {config.get_recordings_path()}")
        print(f"   OBS connection info available: {bool(config.get_obs_connection_info())}")
        print(f"   YouTube API key available: {bool(config.get_youtube_api_key())}")
        return True
    except Exception as e:
        print(f"❌ Config test failed: {e}")
        return False

def test_file_structure():
    """Test file structure and permissions"""
    print("\nTesting file structure...")
    
    required_files = [
        'main.py',
        'config.py',
        'obs_controller.py',
        'youtube_api.py',
        'recording_manager.py',
        'requirements.txt',
        '.env.example'
    ]
    
    all_present = True
    for file in required_files:
        if Path(file).exists():
            print(f"✅ {file} exists")
        else:
            print(f"❌ {file} missing")
            all_present = False
    
    return all_present

def main():
    """Run all basic tests"""
    print("StreamAI Recording App - Basic Tests")
    print("=" * 40)
    
    tests = [
        ("Module Imports", test_imports),
        ("Configuration", test_config),
        ("File Structure", test_file_structure)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        result = test_func()
        results.append((test_name, result))
    
    print("\n" + "=" * 40)
    print("Test Results Summary:")
    
    all_passed = True
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if not result:
            all_passed = False
    
    if all_passed:
        print("\n🎉 All basic tests passed!")
        print("The core application structure is ready.")
        print("\nNext steps:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Configure .env file with your API keys")
        print("3. Set up OBS WebSocket connection")
        print("4. Run: python main.py test")
    else:
        print("\n⚠️  Some tests failed. Please check the issues above.")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
