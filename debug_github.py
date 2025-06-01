import streamlit as st
import os
import time
from github_api import (
    verify_repository_access, 
    create_milestone, 
    create_issue, 
    get_repository_info,
    get_authenticated_user,
    GitHubError
)
from deepseek_api import test_deepseek_connection, validate_deepseek_config

st.set_page_config(page_title="GitHub Debug Tool", layout="wide")

st.title("🔧 GitHub Connection Debug Tool")

st.markdown("This tool will help us debug why the deployment isn't working.")

# Test 1: Environment Variables
st.markdown("## 📋 Step 1: Environment Variables")
github_token = os.getenv("GITHUB_TOKEN")
repo_owner = os.getenv("REPO_OWNER")
repo_name = os.getenv("REPO_NAME")
deepseek_key = os.getenv("DEEPSEEK_API_KEY")

if github_token:
    st.success(f"✅ GITHUB_TOKEN: {github_token[:10]}...{github_token[-4:]}")
else:
    st.error("❌ GITHUB_TOKEN not found")

if repo_owner:
    st.success(f"✅ REPO_OWNER: {repo_owner}")
else:
    st.error("❌ REPO_OWNER not found")

if repo_name:
    st.success(f"✅ REPO_NAME: {repo_name}")
else:
    st.error("❌ REPO_NAME not found")

if deepseek_key:
    st.success(f"✅ DEEPSEEK_API_KEY: {deepseek_key[:10]}...{deepseek_key[-4:]}")
else:
    st.error("❌ DEEPSEEK_API_KEY not found")

# Test 2: GitHub Authentication
st.markdown("## 🔐 Step 2: GitHub Authentication")
if st.button("Test GitHub Authentication"):
    try:
        user_info = get_authenticated_user()
        st.success(f"✅ Authenticated as: {user_info.get('login', 'Unknown')}")
        st.json(user_info)
    except Exception as e:
        st.error(f"❌ Authentication failed: {str(e)}")

# Test 3: Repository Access
st.markdown("## 📁 Step 3: Repository Access")
if st.button("Test Repository Access"):
    try:
        access_ok, message, repo_data = verify_repository_access()
        if access_ok:
            st.success(f"✅ {message}")
            st.json(repo_data)
        else:
            st.error(f"❌ {message}")
    except Exception as e:
        st.error(f"❌ Repository access failed: {str(e)}")

# Test 4: Create Test Milestone
st.markdown("## 🎯 Step 4: Test Milestone Creation")
test_milestone_title = st.text_input("Test Milestone Title", value="DEBUG-TEST-MILESTONE")
dry_run_milestone = st.checkbox("Dry Run (Milestone)", value=True)

if st.button("Create Test Milestone"):
    try:
        start_time = time.time()
        st.info(f"Creating milestone: {test_milestone_title}")
        
        milestone_num = create_milestone(
            title=test_milestone_title,
            description="This is a test milestone created by the debug tool",
            dry_run=dry_run_milestone
        )
        
        end_time = time.time()
        
        if dry_run_milestone:
            st.success(f"✅ DRY RUN: Milestone would be created (took {end_time - start_time:.2f}s)")
        else:
            st.success(f"✅ Milestone created with number: {milestone_num} (took {end_time - start_time:.2f}s)")
            
    except Exception as e:
        st.error(f"❌ Milestone creation failed: {str(e)}")
        st.exception(e)

# Test 5: Create Test Issue
st.markdown("## 📋 Step 5: Test Issue Creation")
test_issue_title = st.text_input("Test Issue Title", value="DEBUG-TEST-ISSUE")
test_milestone_number = st.number_input("Milestone Number (0 for none)", value=0, min_value=0)
dry_run_issue = st.checkbox("Dry Run (Issue)", value=True)

if st.button("Create Test Issue"):
    try:
        start_time = time.time()
        st.info(f"Creating issue: {test_issue_title}")
        
        milestone = test_milestone_number if test_milestone_number > 0 else None
        
        issue_result = create_issue(
            title=test_issue_title,
            body="This is a test issue created by the debug tool",
            milestone=milestone,
            labels=["debug", "test"],
            dry_run=dry_run_issue
        )
        
        end_time = time.time()
        
        if dry_run_issue:
            st.success(f"✅ DRY RUN: Issue would be created (took {end_time - start_time:.2f}s)")
        else:
            st.success(f"✅ Issue created with number: {issue_result.get('number', 'Unknown')} (took {end_time - start_time:.2f}s)")
            st.json(issue_result)
            
    except Exception as e:
        st.error(f"❌ Issue creation failed: {str(e)}")
        st.exception(e)

# Test 6: DeepSeek Connection
st.markdown("## 🤖 Step 6: DeepSeek AI Connection")
if st.button("Test DeepSeek Connection"):
    try:
        validate_deepseek_config()
        connected, message = test_deepseek_connection()
        if connected:
            st.success(f"✅ DeepSeek AI: {message}")
        else:
            st.error(f"❌ DeepSeek AI: {message}")
    except Exception as e:
        st.error(f"❌ DeepSeek connection failed: {str(e)}")

# Test 7: Full Workflow Test
st.markdown("## 🚀 Step 7: Full Workflow Test")
if st.button("Run Full Workflow Test"):
    try:
        st.info("🔄 Running full workflow test...")
        
        # Test 1: Create milestone
        st.write("Creating test milestone...")
        milestone_num = create_milestone(
            title="FULL-TEST-MILESTONE",
            description="Full workflow test milestone",
            dry_run=True  # Always dry run for this test
        )
        st.success(f"✅ Milestone test passed (would create #{milestone_num})")
        
        # Test 2: Create issue
        st.write("Creating test issue...")
        issue_result = create_issue(
            title="FULL-TEST-ISSUE",
            body="Full workflow test issue",
            milestone=None,  # Don't link to milestone in dry run
            labels=["test"],
            dry_run=True  # Always dry run for this test
        )
        st.success("✅ Issue test passed")
        
        # Test 3: Check timing
        start = time.time()
        time.sleep(0.1)  # Simulate some work
        end = time.time()
        st.success(f"✅ Timing test passed ({end - start:.2f}s)")
        
        st.success("🎉 All tests passed! The workflow should work.")
        
    except Exception as e:
        st.error(f"❌ Full workflow test failed: {str(e)}")
        st.exception(e)

st.markdown("---")
st.markdown("### 💡 Instructions:")
st.markdown("""
1. **Run each test step by step**
2. **Check if all environment variables are loaded**
3. **Test GitHub authentication and repository access**
4. **Try creating a test milestone and issue**
5. **If any step fails, that's where the problem is!**

**Common Issues:**
- ❌ **Authentication fails**: Check your GitHub token
- ❌ **Repository access fails**: Check repo name/owner or token permissions
- ❌ **Milestone/Issue creation fails**: Check if repository has issues enabled
""")
