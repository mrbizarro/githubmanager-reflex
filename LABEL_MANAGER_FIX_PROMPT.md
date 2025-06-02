**PROMPT FOR NEXT AI:**

**TASK: Fix Label Manager - Simplify to Remove Non-Standard Labels Only**

**PROBLEM:** 
The current label management system in the Repository Cleanup page is overly complex and not working as intended. We need to simplify it to do one thing well: remove all non-standard GitHub labels so users can run the modern label setup cleanly.

**CURRENT ISSUE:**
- The label analysis and deletion functions are mock implementations
- Complex categorization system is confusing users
- Users just want to clean up old labels before applying the modern label system
- The "suggested deletions" logic is not actually implemented

**REQUIRED SOLUTION:**
Create a simple, working label cleanup system that:

1. **Loads all labels** from the repository using the real GitHub API
2. **Identifies standard GitHub labels** (keep these safe)
3. **Shows all non-standard labels** for deletion
4. **Provides bulk delete functionality** for non-standard labels
5. **Works with real GitHub API calls** (not mock data)

**STANDARD GITHUB LABELS TO KEEP:**
```
- bug
- documentation  
- duplicate
- enhancement
- good first issue
- help wanted
- invalid
- question
- wontfix
```

**IMPLEMENTATION REQUIREMENTS:**

**File to Modify:** `pages/repository_cleanup.py`

**Functions to Fix:**
1. `analyze_repository_labels()` - Make it load real labels from GitHub API
2. `delete_suggested_labels()` - Implement real label deletion
3. `delete_custom_labels()` - Implement real label deletion
4. Simplify the `render_label_analysis()` to show only:
   - Standard labels (keep these)
   - Non-standard labels (delete these)

**Simple UI Flow:**
```
1. Click "Load & Analyze Labels"
2. Show two lists:
   ✅ Standard Labels (X labels) - These will be kept
   🗑️ Non-Standard Labels (X labels) - These will be deleted
3. Button: "🗑️ Delete All Non-Standard Labels"
4. Confirmation: "This will delete X labels. Continue?"
5. Progress bar during deletion
6. Success message: "Deleted X labels. Ready for modern label setup!"
```

**API Integration:**
- Use existing `utils.github_api.GitHubAPI` class
- Add method `get_labels()` if it doesn't exist
- Add method `delete_label(label_name)` if it doesn't exist
- Handle rate limiting with delays between deletions

**Error Handling:**
- Show clear errors if GitHub API fails
- Continue deleting other labels if one fails
- Display summary of successful/failed deletions

**Testing:**
After implementation, users should be able to:
1. Load their repository labels
2. See exactly which labels are standard vs non-standard
3. Delete all non-standard labels with one click
4. Run the modern label setup cleanly on a repository with only standard labels

**KEEP IT SIMPLE:** 
Remove all the complex categorization (project labels, duplicate candidates, etc.). Just focus on: Standard vs Non-Standard. Delete the non-standard ones. Done.

**Current File Location:** `C:\vibecode\githubmanager\pages\repository_cleanup.py`

**Expected Outcome:** 
A working label cleanup system that actually connects to GitHub API and removes non-standard labels, preparing the repository for a clean modern label setup.
