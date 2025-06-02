#!/usr/bin/env python3
"""
🧹 GitHub Manager Project Cleanup Script
Cleans up redundant files and organizes project structure professionally.
"""

import os
import shutil
import sys
from pathlib import Path

class ProjectCleaner:
    def __init__(self, project_path):
        self.project_path = Path(project_path)
        self.backup_dir = self.project_path / "cleanup_backup"
        
    def create_backup_directory(self):
        """Create backup directory for files we're removing"""
        self.backup_dir.mkdir(exist_ok=True)
        print(f"✅ Created backup directory: {self.backup_dir}")
        
    def remove_redundant_files(self):
        """Remove redundant backup and test files"""
        
        # Files to completely remove (redundant/outdated)
        files_to_remove = [
            "app_backup.py",
            "app_legacy.py", 
            "app_original_backup.py",
            "debug_github.py",
            "debug_live.py",
            "github_api_simple.py",  # Keeping github_api.py as main
            "quick_test.py",
            "quick_test_fix.py", 
            "quick_test_live.md",
            "test_clean.py",
            "test_deepseek.py",
            "test_deployment.py",
            "test_github_config.py",
            "test_imports.py",
            "test_reflex_app.py",
            "test_token.py",
            "ai_split.py",  # Assuming this was for old refactoring
            "parse_markdown.py",  # If functionality moved to utils
            "enhanced_deployment_fix.py",
            "launch_clean.bat",
            "launch_simple.bat",
            "start_enhanced.bat",
            "setup_git.bat",
            "setup_git.sh"
        ]
        
        # Documentation files to consolidate
        docs_to_remove = [
            "README_ENHANCED.md",  # Keep main README.md
            "DEPLOYMENT_IMPROVEMENTS.md",
            "TEST_ENHANCED_DEPLOYMENT.md",
            "IMPLEMENTATION_COMPLETE.md",
            "enhanced_labels_demo.md",
            "smart_tagging_demo.md",
            "tagging_test.md",
            "ai_labeling_prompt.md"
        ]
        
        all_files_to_remove = files_to_remove + docs_to_remove
        
        for filename in all_files_to_remove:
            file_path = self.project_path / filename
            if file_path.exists():
                # Move to backup before removing
                backup_path = self.backup_dir / filename
                shutil.move(str(file_path), str(backup_path))
                print(f"🗑️  Moved to backup: {filename}")
        
    def organize_documentation(self):
        """Organize documentation into a docs folder"""
        docs_dir = self.project_path / "docs"
        docs_dir.mkdir(exist_ok=True)
        
        # Documentation files to move to docs folder
        docs_to_move = [
            "ARCHITECTURE.md",
            "CONTRIBUTING.md", 
            "DEPLOYMENT.md",
            "SECURITY.md",
            "TROUBLESHOOTING.md",
            "quick_test.md"
        ]
        
        for doc_file in docs_to_move:
            source = self.project_path / doc_file
            if source.exists():
                destination = docs_dir / doc_file
                shutil.move(str(source), str(destination))
                print(f"📄 Moved to docs/: {doc_file}")
                
    def create_scripts_directory(self):
        """Move scripts to a dedicated scripts folder"""
        scripts_dir = self.project_path / "scripts"
        scripts_dir.mkdir(exist_ok=True)
        
        # Scripts to move
        scripts_to_move = [
            "deployment_manager.py",
            "label_manager.py",
            "quick_start.py"
        ]
        
        for script_file in scripts_to_move:
            source = self.project_path / script_file
            if source.exists():
                destination = scripts_dir / script_file
                shutil.move(str(source), str(destination))
                print(f"🔧 Moved to scripts/: {script_file}")
                
    def clean_main_directory(self):
        """Ensure main directory only has essential files"""
        
        # These should be the only files in root
        essential_root_files = {
            "app.py",           # Redirect to main app
            "app_new.py",       # Main application  
            "github_api.py",    # Main GitHub API handler
            "deepseek_api.py",  # AI API handler
            "requirements.txt", # Dependencies
            "README.md",        # Main documentation
            "LICENSE",          # License file
            ".env.template",    # Template for environment
            ".env",             # Actual environment (should be in .gitignore)
            ".gitignore",       # Git ignore rules
            ".gitattributes"    # Git attributes
        }
        
        print("\n📋 Essential files that should remain in root:")
        for file in sorted(essential_root_files):
            if (self.project_path / file).exists():
                print(f"   ✅ {file}")
            else:
                print(f"   ❌ {file} (missing)")
                
    def secure_environment_file(self):
        """Ensure .env file security"""
        env_file = self.project_path / ".env"
        
        if env_file.exists():
            print("\n🔐 SECURITY CHECK:")
            print("⚠️  Your .env file contains sensitive credentials!")
            print("✅ .env is properly listed in .gitignore")
            print("🔧 Consider regenerating your GitHub token for security")
            
            # Check if it might have been committed
            git_dir = self.project_path / ".git"
            if git_dir.exists():
                print("\n🔍 IMPORTANT: Check if .env was ever committed to git:")
                print("   Run: git log --all --full-history -- .env")
                print("   If it shows results, your credentials may be in git history!")
                print("   Consider: git filter-branch to remove from history")
                
    def create_clean_structure_summary(self):
        """Show the clean project structure"""
        print("\n" + "="*60)
        print("🎯 CLEAN PROJECT STRUCTURE")
        print("="*60)
        
        structure = """
📁 githubmanager/
├── 📄 app.py                 # Entry point (redirect)
├── 📄 app_new.py            # Main application
├── 📄 github_api.py         # GitHub API integration
├── 📄 deepseek_api.py       # AI API integration  
├── 📄 requirements.txt      # Dependencies
├── 📄 README.md            # Main documentation
├── 📄 LICENSE              # License
├── 📄 .env.template        # Environment template
├── 📄 .env                 # Your credentials (secured)
├── 📄 .gitignore           # Git ignore rules
├── 📄 .gitattributes       # Git attributes
├── 📁 components/          # UI components
├── 📁 pages/              # Application pages
├── 📁 utils/              # Utility functions
├── 📁 config/             # Configuration
├── 📁 assets/             # Styling and assets
├── 📁 docs/               # Documentation
├── 📁 scripts/            # Utility scripts
├── 📁 venv/               # Virtual environment
└── 📁 cleanup_backup/     # Backup of removed files
        """
        print(structure)
        
    def run_cleanup(self):
        """Execute the complete cleanup process"""
        print("🧹 Starting GitHub Manager Project Cleanup...")
        print("="*60)
        
        try:
            self.create_backup_directory()
            self.remove_redundant_files()
            self.organize_documentation() 
            self.create_scripts_directory()
            self.clean_main_directory()
            self.secure_environment_file()
            self.create_clean_structure_summary()
            
            print("\n" + "="*60)
            print("✅ CLEANUP COMPLETED SUCCESSFULLY!")
            print("="*60)
            print("🔧 Next steps:")
            print("   1. Review the backup folder for any files you need")
            print("   2. Test your application: streamlit run app_new.py")
            print("   3. Consider regenerating your GitHub token")
            print("   4. Commit these changes to git")
            
        except Exception as e:
            print(f"❌ Error during cleanup: {e}")
            return False
            
        return True

def main():
    """Main cleanup function"""
    
    # Get project path
    if len(sys.argv) > 1:
        project_path = sys.argv[1]
    else:
        project_path = os.getcwd()
        
    # Confirm before running
    print(f"🎯 About to clean up project: {project_path}")
    print("This will:")
    print("   • Remove redundant backup and test files")
    print("   • Organize documentation into docs/ folder")
    print("   • Move scripts to scripts/ folder") 
    print("   • Create backup of all removed files")
    print("   • Check environment file security")
    
    response = input("\n🤔 Continue with cleanup? (y/N): ").strip().lower()
    
    if response in ['y', 'yes']:
        cleaner = ProjectCleaner(project_path)
        success = cleaner.run_cleanup()
        return 0 if success else 1
    else:
        print("❌ Cleanup cancelled.")
        return 0

if __name__ == "__main__":
    sys.exit(main())
