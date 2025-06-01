#!/usr/bin/env python3
"""
Quick test to verify DeepSeek API is working after fixing the .env file
"""

import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get the API key
api_key = os.getenv("DEEPSEEK_API_KEY")

print("🧪 Quick DeepSeek API Test")
print("=" * 40)
print(f"API Key found: {'✅ Yes' if api_key else '❌ No'}")

if api_key:
    print(f"API Key (first 10 chars): {api_key[:10]}...")
    print(f"API Key (last 5 chars): ...{api_key[-5:]}")
    
    # Test basic API call
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {
                "role": "user",
                "content": "Just respond with 'OK' if you can read this message."
            }
        ],
        "temperature": 0.3,
        "max_tokens": 10,
        "stream": False
    }
    
    try:
        print("\n🔌 Testing API connection...")
        response = requests.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30  # Increased timeout
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            content = data.get('choices', [{}])[0].get('message', {}).get('content', '')
            print(f"✅ SUCCESS! API Response: '{content}'")
        else:
            print(f"❌ FAILED! Response: {response.text}")
            
    except requests.exceptions.Timeout:
        print("❌ TIMEOUT: The API request timed out")
        print("💡 This might be a network issue or high server load")
    except requests.exceptions.ConnectionError:
        print("❌ CONNECTION ERROR: Could not connect to DeepSeek API")
        print("💡 Check your internet connection")
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")

else:
    print("❌ No API key found in .env file")

print("\n💡 If you're still having issues:")
print("- Check your internet connection")
print("- Verify the API key is correct on https://platform.deepseek.com")
print("- Try running the app again with the fixed .env file")
