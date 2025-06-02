#!/usr/bin/env python3
"""
Clean test to verify the app works
"""

try:
    print("🧪 Testing GitHub Issues Manager v6...")
    
    # Test all imports
    from config.settings import get_config, Config, check_basic_config
    from components.status import render_status_section
    from components.header import render_header  
    from components.navigation import render_navigation
    from pages.upload_convert import render_upload_page
    from pages.manual_entry import render_manual_page
    from pages.repository_cleanup import render_cleanup_page
    
    print("✅ All imports successful!")
    
    # Test basic functionality
    config = check_basic_config()
    print(f"✅ Config check: GitHub={config['github_configured']}, AI={config['ai_configured']}")
    
    print("🎉 App is ready to launch!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
