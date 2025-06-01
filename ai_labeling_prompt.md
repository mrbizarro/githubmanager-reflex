# AI Labeling System Prompt

## Objective
Enhance the GitHub issue creation system to automatically assign intelligent labels based on content analysis, priority assessment, and categorization.

## System Requirements

### 1. Priority-Based Labels
Analyze issue content and assign priority levels:
- **🔴 critical**: System-breaking, security vulnerabilities, production down
- **🟠 high**: Major features, significant bugs affecting many users
- **🟡 medium**: Standard features, moderate bugs, improvements
- **🟢 low**: Minor enhancements, documentation, nice-to-have features
- **🔵 backlog**: Future considerations, research items

### 2. Category-Based Labels
Classify issues by type and domain:

**Type Categories:**
- **bug**: Defects, errors, unexpected behavior
- **feature**: New functionality, enhancements
- **documentation**: Docs, README, guides, comments
- **refactor**: Code cleanup, optimization, restructuring
- **test**: Testing, QA, automation
- **maintenance**: Dependencies, updates, housekeeping
- **security**: Vulnerabilities, authentication, authorization

**Domain Categories:**
- **frontend**: UI, UX, client-side code
- **backend**: Server-side, APIs, databases
- **infrastructure**: DevOps, deployment, CI/CD
- **mobile**: Mobile app development
- **desktop**: Desktop application features
- **api**: API development and integration
- **database**: Database design, queries, migrations

**Status Categories:**
- **ready**: Ready for development
- **blocked**: Waiting on dependencies
- **research**: Needs investigation
- **wip**: Work in progress
- **review**: Ready for code review

### 3. Effort Estimation Labels
Estimate development effort:
- **effort/xs**: < 1 hour (tiny fixes, typos)
- **effort/s**: 1-4 hours (small features, minor bugs)
- **effort/m**: 1-3 days (medium features, complex bugs)
- **effort/l**: 1-2 weeks (large features, major refactors)
- **effort/xl**: > 2 weeks (epic features, architectural changes)

### 4. Impact Assessment Labels
Assess user/business impact:
- **impact/critical**: Affects all users, business critical
- **impact/high**: Affects many users, important features
- **impact/medium**: Affects some users, standard features
- **impact/low**: Affects few users, minor improvements

## Implementation Instructions

### Step 1: Enhanced AI Analysis Function
Create a new function in `deepseek_api.py`:

```python
def analyze_issue_labels(issue_title: str, issue_body: str, milestone_context: str = "") -> List[str]:
    """
    Use AI to analyze issue content and suggest appropriate labels.
    
    Args:
        issue_title: The issue title
        issue_body: The issue description/body
        milestone_context: Context from the milestone description
        
    Returns:
        List of suggested labels
    """
```

### Step 2: AI Prompt Template
Use this prompt structure for the AI analysis:

```
You are an expert project manager analyzing GitHub issues. Based on the content below, suggest appropriate labels from the predefined categories.

ISSUE TITLE: {title}
ISSUE BODY: {body}
MILESTONE CONTEXT: {milestone_context}

AVAILABLE LABEL CATEGORIES:

Priority (choose one):
- critical, high, medium, low, backlog

Type (choose 1-2):
- bug, feature, documentation, refactor, test, maintenance, security

Domain (choose 1-2):
- frontend, backend, infrastructure, mobile, desktop, api, database

Status (choose one):
- ready, blocked, research, wip, review

Effort (choose one):
- effort/xs, effort/s, effort/m, effort/l, effort/xl

Impact (choose one):
- impact/critical, impact/high, impact/medium, impact/low

ANALYSIS RULES:
1. Always assign exactly one priority label
2. Always assign exactly one effort label
3. Always assign exactly one impact label
4. Assign 1-2 type labels (primary type + secondary if applicable)
5. Assign 1-2 domain labels if technical content is present
6. Assign one status label (default to "ready" unless specified otherwise)
7. Use keywords, urgency indicators, and context clues
8. Consider technical complexity for effort estimation
9. Consider user base size for impact assessment

KEYWORD INDICATORS:
- Critical: "urgent", "production", "security", "down", "broken", "blocker"
- High: "important", "major", "significant", "asap", "priority"
- Bug: "error", "bug", "issue", "problem", "broken", "fails", "doesn't work"
- Feature: "add", "implement", "create", "new", "enhance", "improvement"
- Frontend: "UI", "interface", "design", "styling", "component", "page"
- Backend: "API", "server", "database", "logic", "service", "endpoint"

Respond with only a comma-separated list of labels, no explanation.
```

### Step 3: Integration Points

#### Update `ai_split.py`:
Add label analysis to the existing AI parsing:

```python
def ai_split_with_labels(markdown_content: str) -> Tuple[str, Dict[str, Any]]:
    # Existing parsing logic...
    
    # For each issue, add label analysis
    for milestone_name, milestone_data in structure.items():
        for issue in milestone_data.get('issues', []):
            suggested_labels = analyze_issue_labels(
                issue['title'], 
                issue['body'], 
                milestone_data.get('description', '')
            )
            # Merge with existing labels, AI suggestions take precedence
            existing_labels = set(issue.get('labels', []))
            ai_labels = set(suggested_labels)
            issue['labels'] = list(existing_labels.union(ai_labels))
```

#### Update `parse_markdown.py`:
Integrate label analysis into the main parsing flow:

```python
def parse_markdown(md_text: str, use_ai: bool = True) -> Tuple[str, Dict[str, Any]]:
    if use_ai:
        reasoning, project = ai_split_with_labels(md_text)
    else:
        # Traditional parsing with basic label analysis
        reasoning, project = traditional_parse_with_labels(md_text)
    
    return reasoning, project
```

### Step 4: UI Enhancements

#### Update `app.py` label editing section:
```python
# Enhanced label input with suggestions
suggested_labels = iss.get('labels', [])
label_categories = {
    'Priority': ['critical', 'high', 'medium', 'low', 'backlog'],
    'Type': ['bug', 'feature', 'documentation', 'refactor', 'test', 'maintenance', 'security'],
    'Domain': ['frontend', 'backend', 'infrastructure', 'mobile', 'desktop', 'api', 'database'],
    'Effort': ['effort/xs', 'effort/s', 'effort/m', 'effort/l', 'effort/xl'],
    'Impact': ['impact/critical', 'impact/high', 'impact/medium', 'impact/low']
}

# Show current AI suggestions
if suggested_labels:
    st.info(f"🤖 AI Suggested: {', '.join(suggested_labels)}")

# Category-based label selection
for category, options in label_categories.items():
    current_selection = [l for l in suggested_labels if l in options]
    selected = st.multiselect(
        f"{category} Labels",
        options,
        default=current_selection,
        key=f"{category}_{m_title}_{idx}"
    )
    # Update the issue labels
    iss['labels'] = [l for l in iss['labels'] if l not in options] + selected
```

### Step 5: Configuration Options

Add to sidebar settings:

```python
st.subheader("🏷️ Label Configuration")
auto_labels = st.checkbox(
    "Auto-generate labels", 
    value=True,
    help="Use AI to automatically suggest labels based on content"
)

label_strictness = st.selectbox(
    "Label Strictness",
    ["Conservative", "Balanced", "Aggressive"],
    index=1,
    help="How many labels to suggest"
)
```

### Step 6: Label Validation

Add label validation in `github_api.py`:

```python
def validate_and_create_labels(labels: List[str], dry_run: bool = False) -> List[str]:
    """
    Validate labels and create any missing ones in the repository.
    """
    valid_labels = []
    predefined_colors = {
        'critical': 'B60205',
        'high': 'D93F0B', 
        'medium': 'FBCA04',
        'low': '0E8A16',
        'bug': 'D73A4A',
        'feature': '0075CA',
        'documentation': '0075CA',
        # ... more predefined colors
    }
    
    for label in labels:
        if not dry_run:
            # Check if label exists, create if not
            color = predefined_colors.get(label.split('/')[0], 'EDEDED')
            ensure_label_exists(label, color)
        valid_labels.append(label)
    
    return valid_labels
```

## Expected Outcomes

1. **Consistent Labeling**: All issues get properly categorized labels
2. **Better Project Management**: Clear priority and effort indicators
3. **Improved Filtering**: Easy to find issues by category/priority
4. **Automated Workflow**: Reduces manual labeling overhead
5. **Enhanced Visibility**: Better project overview and planning

## Testing Strategy

1. **Test with various markdown formats**: Technical docs, user stories, bug reports
2. **Validate label accuracy**: Manual review of AI suggestions
3. **Performance testing**: Ensure labeling doesn't slow down processing
4. **Edge case handling**: Empty content, very long descriptions, mixed content

## Future Enhancements

1. **Learning System**: Track label accuracy and improve over time
2. **Custom Categories**: Allow users to define custom label categories
3. **Team Preferences**: Save team-specific labeling patterns
4. **Integration**: Connect with project management tools
5. **Analytics**: Label-based project insights and reporting

This enhancement will significantly improve the utility and organization of generated GitHub issues while maintaining the simplicity of the current workflow.
