#!/usr/bin/env python3
"""
Test script for DeepSeek AI integration
Run this to verify your DeepSeek API configuration
"""

import os
from dotenv import load_dotenv
from deepseek_api import test_deepseek_connection, ai_parse_markdown, DeepSeekError

def test_deepseek():
    """Test DeepSeek API connection and basic functionality"""
    
    print("🧪 Testing DeepSeek AI Integration...")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    # Test 1: Check API key
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        print("❌ DEEPSEEK_API_KEY not found in .env file")
        print("💡 Please add your DeepSeek API key to the .env file")
        return False
    else:
        print("✅ DeepSeek API key found")
    
    # Test 2: Test connection
    print("\n🔌 Testing API connection...")
    try:
        connected, message = test_deepseek_connection()
        if connected:
            print(f"✅ {message}")
        else:
            print(f"❌ {message}")
            return False
    except Exception as e:
        print(f"❌ Connection test failed: {str(e)}")
        return False
    
    # Test 3: Test AI parsing with sample markdown
    print("\n🧠 Testing AI parsing...")
    sample_markdown = """
# Project Launch

We need to prepare for the product launch next month.

## Website Updates
- Update landing page
- Add new product information
- Optimize for mobile

## Marketing Campaign  
- Create social media content
- Design email templates
- Plan launch event

## Bug Fixes
- Fix login issues
- Resolve payment gateway problems
- Update user dashboard
"""
    
    try:
        reasoning, structure = ai_parse_markdown(sample_markdown)
        
        print("✅ AI parsing successful!")
        print(f"\n🤔 AI Reasoning (first 200 chars):")
        print(f"{reasoning[:200]}...")
        
        print(f"\n📊 Parsed Structure:")
        print(f"- Milestones found: {len(structure)}")
        
        total_issues = sum(len(milestone.get('issues', [])) for milestone in structure.values())
        print(f"- Total issues: {total_issues}")
        
        for milestone_name in structure.keys():
            print(f"  • {milestone_name}")
        
        return True
        
    except DeepSeekError as e:
        print(f"❌ AI parsing failed: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error during AI parsing: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_deepseek()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 All tests passed! DeepSeek AI is ready to use.")
        print("💡 You can now run 'streamlit run app.py' to start the application.")
    else:
        print("❌ Tests failed. Please check your configuration.")
        print("💡 Make sure your .env file has the correct DEEPSEEK_API_KEY")
    
    print("\n🔧 Need help?")
    print("- Check your .env file configuration")
    print("- Verify your DeepSeek API key at https://platform.deepseek.com")
    print("- Make sure you have internet connectivity")
