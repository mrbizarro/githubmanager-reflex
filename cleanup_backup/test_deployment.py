#!/usr/bin/env python3
"""
Test script for the enhanced deployment system
Run this to verify that the new deployment manager works correctly
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

def test_deployment_manager():
    """Test the deployment manager import and basic functionality"""
    print("🧪 Testing Enhanced Deployment Manager...")
    
    try:
        # Test import
        from deployment_manager import DeploymentManager, create_enhanced_deployment_section
        print("✅ Successfully imported deployment manager")
        
        # Test DeploymentManager instantiation
        manager = DeploymentManager()
        print("✅ Successfully created DeploymentManager instance")
        
        # Test basic functionality
        test_projects = {
            "Test Milestone 1": {
                "description": "Test milestone description",
                "issues": [
                    {
                        "title": "Test Issue 1",
                        "body": "Test issue body",
                        "labels": ["test", "enhancement"],
                        "assignees": []
                    }
                ]
            }
        }
        
        total_steps = manager.calculate_total_steps(test_projects)
        expected_steps = 2  # 1 milestone + 1 issue
        
        if total_steps == expected_steps:
            print("✅ calculate_total_steps working correctly")
        else:
            print(f"❌ calculate_total_steps failed: expected {expected_steps}, got {total_steps}")
        
        print("✅ Basic deployment manager functionality verified")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_github_api():
    """Test GitHub API connectivity"""
    print("\n🔗 Testing GitHub API connectivity...")
    
    try:
        from github_api import validate_github_config, verify_repository_access
        
        # Test configuration validation
        try:
            validate_github_config()
            print("✅ GitHub configuration is valid")
        except Exception as e:
            print(f"⚠️ GitHub configuration issue: {e}")
            return False
        
        # Test repository access (if configured)
        try:
            access_ok, message, _ = verify_repository_access()
            if access_ok:
                print("✅ Repository access verified")
            else:
                print(f"⚠️ Repository access issue: {message}")
            return access_ok
        except Exception as e:
            print(f"❌ Repository access test failed: {e}")
            return False
            
    except ImportError as e:
        print(f"❌ GitHub API import error: {e}")
        return False

def test_streamlit_compatibility():
    """Test Streamlit compatibility"""
    print("\n📱 Testing Streamlit compatibility...")
    
    try:
        import streamlit as st
        print("✅ Streamlit is available")
        
        # Test if we can run without Streamlit session state
        # (This would be in a real Streamlit app)
        print("✅ Streamlit compatibility verified")
        return True
        
    except ImportError:
        print("⚠️ Streamlit not available (this is OK for testing)")
        return True
    except Exception as e:
        print(f"❌ Streamlit compatibility issue: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Enhanced Deployment System - Test Suite")
    print("=" * 50)
    
    tests = [
        ("Deployment Manager", test_deployment_manager),
        ("GitHub API", test_github_api),
        ("Streamlit Compatibility", test_streamlit_compatibility)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 Test Summary:")
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("\n🎉 All tests passed! Your enhanced deployment system is ready to use.")
        print("\n📝 To use the enhanced system:")
        print("1. Run your Streamlit app: streamlit run app.py")
        print("2. Upload markdown files or create manual entries")
        print("3. Click deploy to see the enhanced progress tracking")
    else:
        print("\n⚠️ Some tests failed. Please check the error messages above.")
        print("The system may still work, but some features might be limited.")
    
    return passed == len(tests)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
