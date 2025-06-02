#!/usr/bin/env python3
"""Quick test to check if the icon issue is fixed"""

import sys
import traceback
from pathlib import Path
import os

# Change to the reflex app directory
reflex_dir = Path(__file__).parent / "reflex-version"
if reflex_dir.exists():
    os.chdir(reflex_dir)
    sys.path.insert(0, str(reflex_dir))

def test_quick_fix():
    """Test the specific issue that was failing"""
    print("🔍 Testing section_header fix...")
    
    try:
        from githubmanager_reflex.components.ui import section_header
        
        # Test section_header with no icon (this was causing the error)
        header_comp = section_header(
            title="Test Title",
            description="Test description"
            # No icon parameter - this should work now
        )
        
        print("✅ section_header with no icon works!")
        
        # Test section_header with icon
        header_comp_with_icon = section_header(
            title="Test Title",
            description="Test description",
            icon="info"
        )
        
        print("✅ section_header with icon works!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        traceback.print_exc()
        return False

def test_home_page():
    """Test that home page can be created"""
    print("\n🔍 Testing home page creation...")
    
    try:
        from githubmanager_reflex.pages.home import page as home_page
        
        # This was failing before
        home_comp = home_page()
        
        print("✅ Home page creation works!")
        return True
        
    except Exception as e:
        print(f"❌ Home page test failed: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 QUICK FIX VALIDATION")
    print("=" * 30)
    
    test1 = test_quick_fix()
    test2 = test_home_page()
    
    if test1 and test2:
        print("\n🎉 ALL FIXES SUCCESSFUL!")
        print("Your app should now work. Try: reflex run")
    else:
        print("\n❌ Some issues remain.")
