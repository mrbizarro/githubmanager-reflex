"""
🎨 Fix GitHub Repository Labels - Apply Modern Colored Labels
This script will set up the modern colored label system in your GitHub repository
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    """Main function to fix GitHub repository labels"""
    
    print("🎨 GitHub Label Fixer - Modern Colored Labels")
    print("=" * 50)
    
    # Check environment variables
    github_token = os.getenv('GITHUB_TOKEN')
    repo_owner = os.getenv('REPO_OWNER')
    repo_name = os.getenv('REPO_NAME')
    
    if not all([github_token, repo_owner, repo_name]):
        print("❌ Error: Missing environment variables!")
        print("Please ensure your .env file contains:")
        print("- GITHUB_TOKEN=your_github_token")
        print("- REPO_OWNER=your_username_or_org")
        print("- REPO_NAME=your_repository_name")
        return False
    
    print(f"📁 Repository: {repo_owner}/{repo_name}")
    print(f"🔑 Token: {'*' * 20}{github_token[-4:]}")
    print()
    
    try:
        # Import the GitHub API module
        from github_api import setup_modern_labels, verify_repository_access
        
        # Verify repository access first
        print("🔍 Verifying repository access...")
        access_ok, message, repo_data = verify_repository_access()
        
        if not access_ok:
            print(f"❌ Repository access failed: {message}")
            return False
        
        print(f"✅ Repository access verified: {message}")
        print()
        
        # Get user confirmation
        print("⚠️  WARNING: This will create/update labels in your GitHub repository")
        print("📋 Modern labels to be created:")
        print("   🚨 priority-critical (Red)")
        print("   ⚡ priority-high (Orange)")  
        print("   📋 priority-medium (Yellow)")
        print("   📝 priority-low (Green)")
        print("   🧪 testing-qa (Medium Slate Blue)")
        print("   🗄️ database-migration (Sea Green)")
        print("   ⚡ code-quality (Gold)")
        print("   🔍 feature-analysis (Royal Blue)")
        print("   🛠️ tech-stack (Gray)")
        print("   📚 documentation (Lime Green)")
        print("   🐛 bug (Crimson)")
        print("   ✨ enhancement (Medium Purple)")
        print("   🚀 deployment (Tomato)")
        print("   🔒 security (Dark Red)")
        print("   + Priority labels (high/medium/low)")
        print()
        
        response = input("❓ Continue with label setup? (y/N): ").strip().lower()
        if response != 'y':
            print("⏹️  Cancelled by user")
            return False
        
        print("🚀 Setting up modern colored labels...")
        print()
        
        # Run the label setup
        results = setup_modern_labels(dry_run=False)
        
        # Display results
        print("🎉 Label setup completed!")
        print(f"   ✅ Created: {results['created']} labels")
        print(f"   🔄 Updated: {results['updated']} labels")
        print(f"   ⏭️  Skipped: {results['skipped']} labels")
        print(f"   ❌ Errors: {len(results['errors'])} labels")
        
        if results['errors']:
            print("\n❌ Errors encountered:")
            for error in results['errors']:
                print(f"   • {error}")
        
        print()
        if results['created'] > 0 or results['updated'] > 0:
            print("🎨 Your repository now has modern colored labels!")
            print("🔗 Check your GitHub repository labels page to see the results")
            
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure github_api.py is in the current directory")
        return False
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 Success! Your GitHub repository labels have been updated!")
    else:
        print("\n💥 Failed to update repository labels")
    
    input("\nPress Enter to exit...")
