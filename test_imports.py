#!/usr/bin/env python3
"""
Simple test to verify imports work correctly
"""

try:
    print("Testing imports...")
    
    # Test config imports
    from config.settings import get_config, Config, check_basic_config
    print("✅ Config imports successful")
    
    # Test basic functionality
    config = check_basic_config()
    print(f"✅ Basic config check: {config}")
    
    # Test get_config function
    github_connected = get_config('github_connected', False)
    print(f"✅ get_config('github_connected'): {github_connected}")
    
    # Test other page imports
    from pages.upload_convert import render_upload_page
    print("✅ Upload page import successful")
    
    from pages.manual_entry import render_manual_page
    print("✅ Manual entry page import successful")
    
    from pages.repository_cleanup import render_cleanup_page
    print("✅ Cleanup page import successful")
    
    print("\n🎉 All imports successful! App should launch without errors.")
    
except Exception as e:
    print(f"❌ Import error: {e}")
    import traceback
    traceback.print_exc()
