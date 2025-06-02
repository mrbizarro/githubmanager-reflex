import streamlit as st
import os
from github_api import create_milestone, create_issue, GitHubError

st.set_page_config(page_title="Live Deployment Test", layout="wide")

st.title("🔧 Live Deployment Debug Test")

st.markdown("Let's test live deployment with the simplest possible case.")

# Show configuration
st.markdown("## 📋 Configuration")
github_token = os.getenv("GITHUB_TOKEN")
repo_owner = os.getenv("REPO_OWNER") 
repo_name = os.getenv("REPO_NAME")

st.write(f"**Repository**: {repo_owner}/{repo_name}")
st.write(f"**Token**: {github_token[:10] if github_token else 'None'}...{github_token[-4:] if github_token else ''}")

# Test 1: Simple milestone creation
st.markdown("## 🎯 Test 1: Create ONE milestone (LIVE)")

if st.button("Create TEST Milestone (LIVE)", type="primary"):
    st.write("🚀 **STARTING LIVE MILESTONE CREATION**")
    
    try:
        st.write("📝 Calling create_milestone function...")
        
        milestone_num = create_milestone(
            title="TEST-LIVE-MILESTONE",
            description="This is a test milestone created by live deployment debug",
            dry_run=False  # LIVE MODE
        )
        
        st.success(f"✅ **SUCCESS!** Created milestone #{milestone_num}")
        st.write(f"🔗 Check: https://github.com/{repo_owner}/{repo_name}/milestones")
        
    except Exception as e:
        st.error(f"❌ **FAILED**: {str(e)}")
        st.exception(e)

# Test 2: Simple issue creation  
st.markdown("## 📋 Test 2: Create ONE issue (LIVE)")

milestone_num_input = st.number_input("Milestone number (from test above, or 0 for none)", value=0, min_value=0)

if st.button("Create TEST Issue (LIVE)", type="primary"):
    st.write("🚀 **STARTING LIVE ISSUE CREATION**")
    
    try:
        st.write("📝 Calling create_issue function...")
        
        milestone = milestone_num_input if milestone_num_input > 0 else None
        
        issue_result = create_issue(
            title="TEST-LIVE-ISSUE",
            body="This is a test issue created by live deployment debug",
            milestone=milestone,
            labels=["test", "debug"],
            assignees=[],
            dry_run=False  # LIVE MODE
        )
        
        if issue_result:
            issue_num = issue_result.get('number', 'Unknown')
            st.success(f"✅ **SUCCESS!** Created issue #{issue_num}")
            st.write(f"🔗 Check: https://github.com/{repo_owner}/{repo_name}/issues")
            st.json(issue_result)
        else:
            st.error("❌ **FAILED**: create_issue returned None")
        
    except Exception as e:
        st.error(f"❌ **FAILED**: {str(e)}")
        st.exception(e)

# Test 3: Compare dry run vs live
st.markdown("## 🧪 Test 3: Compare Dry Run vs Live")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### Dry Run")
    if st.button("Test Dry Run"):
        try:
            st.write("🧪 Testing dry run...")
            result = create_milestone("DRY-TEST", "Dry run test", dry_run=True)
            st.success(f"✅ Dry run returned: {result}")
        except Exception as e:
            st.error(f"❌ Dry run failed: {str(e)}")

with col2:
    st.markdown("### Live Run")
    if st.button("Test Live Run"):
        try:
            st.write("🚀 Testing live run...")
            result = create_milestone("LIVE-TEST-COMPARE", "Live run test", dry_run=False)
            st.success(f"✅ Live run returned: {result}")
            st.write(f"🔗 Check: https://github.com/{repo_owner}/{repo_name}/milestones")
        except Exception as e:
            st.error(f"❌ Live run failed: {str(e)}")
            st.exception(e)

# Test 4: Manual API call
st.markdown("## 🔗 Test 4: Manual API Call")

if st.button("Test Raw API Call"):
    try:
        import requests
        
        url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/milestones"
        headers = {
            "Authorization": f"token {github_token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }
        data = {
            "title": "RAW-API-TEST",
            "description": "Direct API call test"
        }
        
        st.write("📡 Making direct API call...")
        response = requests.post(url, headers=headers, json=data)
        
        st.write(f"**Status Code**: {response.status_code}")
        st.write(f"**Response**: {response.text}")
        
        if response.status_code == 201:
            st.success("✅ **Raw API call succeeded!**")
            result = response.json()
            st.write(f"Created milestone #{result.get('number', 'Unknown')}")
        else:
            st.error("❌ **Raw API call failed**")
            
    except Exception as e:
        st.error(f"❌ **Raw API test failed**: {str(e)}")
        st.exception(e)

st.markdown("---")
st.markdown("### 💡 Instructions:")
st.markdown("""
1. **Run Test 1** - Try to create a simple milestone
2. **Run Test 2** - Try to create a simple issue  
3. **Run Test 3** - Compare dry run vs live
4. **Run Test 4** - Test raw API call

**If any test works, we know the API connection is fine and the problem is in the main app logic.**
**If all tests fail, the problem is in the GitHub API configuration or permissions.**
""")
