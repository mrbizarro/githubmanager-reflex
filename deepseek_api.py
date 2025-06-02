import os
import requests
from dotenv import load_dotenv
from typing import Dict, List, Any, Optional, Tuple
import json
import time

# Load environment variables
load_dotenv()

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_BASE_URL = "https://api.deepseek.com/v1"

class DeepSeekError(Exception):
    """Custom exception for DeepSeek API errors."""
    def __init__(self, message: str, status_code: Optional[int] = None, response_text: Optional[str] = None):
        self.status_code = status_code
        self.response_text = response_text
        super().__init__(f"{message} (Status: {status_code}): {response_text}")

def validate_deepseek_config() -> None:
    """
    Validate that DeepSeek API configuration is present.
    
    Raises:
        DeepSeekError: If API key is missing
    """
    if not DEEPSEEK_API_KEY:
        raise DeepSeekError("Missing DEEPSEEK_API_KEY in environment variables")

def create_master_prompt(markdown_content: str, content_type: str = "auto") -> str:
    """
    Create an enhanced master prompt for DeepSeek to analyze markdown and convert to GitHub structure.
    Now includes content type analysis and adaptive instructions.
    
    Args:
        markdown_content: The markdown content to analyze
        content_type: Type of content or "auto" for automatic detection
        
    Returns:
        Enhanced, adaptive prompt for DeepSeek
    """
    
    # Auto-detect content type if needed
    if content_type == "auto":
        content_type = detect_content_type(markdown_content)
    
    # Get enhanced components
    content_instructions = get_content_specific_instructions(content_type)
    enhanced_labels = get_enhanced_labels_for_content_type(content_type)
    content_examples = get_content_examples(content_type)
    
    # Build the enhanced prompt
    prompt = f"""You are an expert project manager and GitHub workflow specialist with deep experience in agile development and issue tracking. Your task is to analyze the provided markdown content and convert it into a professional, well-organized GitHub project structure.

{content_instructions}

🎯 ORGANIZATION STRATEGY:
You MUST follow this approach for optimal GitHub project management:

1. **Single Milestone Approach**: Create ONE comprehensive milestone that represents the entire project/phase
2. **Label-Based Categorization**: Use labels to organize different work streams within that milestone
3. **Actionable Issues**: Convert content into specific, implementable tasks with clear acceptance criteria
4. **Professional Structure**: Follow GitHub best practices for issue organization and labeling

{enhanced_labels}

🎯 ANALYSIS METHODOLOGY:

1. **Content Analysis**: Read through the markdown content to identify ONLY what is explicitly stated
2. **Direct Extraction**: Extract tasks, requirements, and features that are clearly mentioned
3. **Milestone Identification**: Use the main themes or project titles actually present in the content
4. **Issue Creation**: Convert only the explicitly stated items into actionable GitHub issues
5. **Label Assignment**: Apply labels based on the actual content areas mentioned in the markdown
6. **NO INFERENCE**: Do not add requirements, features, or details not explicitly stated in the content

⚠️ **CRITICAL: STICK TO THE CONTENT**
- Only create issues for items explicitly mentioned in the markdown
- Do not add "standard" features that aren't mentioned (like error handling, testing, etc.)
- Do not infer technical requirements not stated in the content
- Do not expand on brief descriptions with your own assumptions
- If the markdown says "user login", don't assume password reset, rate limiting, etc.
- Use the exact terminology and scope provided in the original content

📐 OUTPUT FORMAT:

You must respond with a JSON object containing exactly these two fields:

```json
{{
  "reasoning": "Your detailed step-by-step analysis...",
  "structure": {{
    "[Project ID] Main Project Title": {{
      "description": "Comprehensive project description...",
      "state": "open",
      "due_date": null,
      "issues": [...]
    }}
  }}
}}
```

🎯 REASONING SECTION REQUIREMENTS:

Your reasoning must include:
1. **Project Analysis**: What is the main goal/theme of this project?
2. **Scope Assessment**: What are the key areas of work identified?
3. **Milestone Strategy**: Why did you choose this specific milestone structure?
4. **Issue Breakdown**: How did you break content into actionable tasks?
5. **Labeling Logic**: Why did you assign specific labels to each issue?
6. **Priority Assessment**: How did you determine task priorities?

🎯 ISSUE STRUCTURE REQUIREMENTS:

Each issue must have:
- **title**: "[Area] Specific actionable task" (e.g., "[Database] Design user schema")
- **body**: Detailed description with context, acceptance criteria, and technical details
- **labels**: Array of relevant labels (minimum 2, maximum 5 per issue)
- **assignees**: Empty array (will be assigned later)

🎯 CRITICAL GUIDELINES:

**CONTENT-FIRST APPROACH:**
🔍 **Strict Content Adherence**: Only create issues for items explicitly mentioned in the markdown
📝 **No Inference Rule**: Do not add features, requirements, or technical details not stated
🎯 **Original Intent**: Preserve the exact scope and language from the source material
📋 **Direct Extraction**: Convert stated items into actionable issues without expansion
💭 **No Assumptions**: Don't assume standard features (auth, testing, error handling) unless mentioned

**CLAUDE-OPTIMIZED ISSUE SIZING:**
🤖 **Context Window Optimization**: Each issue should be sized for Claude's ~200K token context window
🎯 **One-Session Completion**: Issues should be completable in a single Claude Computer Use session
📏 **Content-Based Scope**: Use the natural groupings and scope present in the original markdown
🧩 **Logical Boundaries**: Group related tasks that are mentioned together in the content
💡 **Self-Contained**: Each issue should contain only what was actually described

**ISSUE SIZE EXAMPLES:**
✅ **Good**: If markdown says "user profile page with editing" → "[Frontend] Build user profile page with edit functionality"
❌ **Bad**: If markdown says "user login" → Don't add password reset, 2FA, rate limiting, etc.

✅ **Good**: If markdown mentions "data visualization dashboard" → Use exactly that scope
❌ **Bad**: Don't add real-time updates, export features, etc. unless specifically mentioned

**DO:**
✅ Create exactly ONE milestone encompassing the entire project
✅ Use milestone names based on the actual project title/theme in the markdown
✅ Create issues only for items explicitly mentioned in the content
✅ Use the exact scope and language provided in the original markdown
✅ Group related tasks that are mentioned together in the content
✅ Preserve the original author's intended priorities and organization
✅ Apply labels based on the actual content areas present in the markdown
✅ Size issues based on the natural boundaries in the original content
✅ Use direct quotes and descriptions from the source material
✅ Maintain the original terminology and technical language used

**DON'T:**
❌ Create multiple separate milestones
❌ Add features, requirements, or technical details not mentioned in the markdown
❌ Infer "standard" features like authentication, testing, error handling unless stated
❌ Expand brief descriptions with your own assumptions about what's needed
❌ Change the scope or complexity beyond what's described
❌ Add implementation details or technical specifications not provided
❌ Assume specific technologies, frameworks, or approaches unless mentioned
❌ Create issues for implied or "obvious" requirements not explicitly stated
❌ Use placeholder or template text not based on the actual content
❌ Mix different project phases unless they're combined in the original content

{content_examples}

🎯 QUALITY STANDARDS FOR {content_type.upper().replace('_', ' ')}:

✅ **Claude-Optimized Issue Requirements:**
- **Perfect Scope**: 2-8 hours of focused development work per issue
- **Content-Based**: Only include requirements explicitly stated in the markdown
- **No Inference**: Do not add features, requirements, or details not mentioned
- **Clear Boundaries**: Use the natural groupings present in the original content
- **Actionable Titles**: Create titles that reflect the actual content described
- **Source-Faithful**: Stay true to the language and scope in the original markdown

✅ **Content Extraction Rules:**
- **Direct Quotes**: Use the actual descriptions provided in the markdown
- **Stated Requirements**: Only include features/tasks explicitly mentioned
- **Original Scope**: Don't expand or reduce the scope described
- **Actual Labels**: Apply labels based on content areas actually present
- **No Assumptions**: Don't assume technical implementations or missing details
- **Preserve Intent**: Maintain the original author's intended scope and priorities

✅ **Project Organization:**
- **Content-Driven Structure**: Organize issues based on the structure present in the markdown
- **Original Priorities**: Maintain any priorities or sequencing indicated in the content
- **Natural Groupings**: Use the logical groupings already present in the source material
- **Scope Preservation**: Keep the exact scope described without expansion or reduction
- **Terminology Consistency**: Use the same terms and language as the original content

✅ **Claude Computer Use Optimization:**
- **Content-Based Scope**: Issues reflect the actual scope described in the markdown
- **Requirement-Faithful**: Each issue contains only what was explicitly stated
- **Source-Driven**: Descriptions based directly on the original content
- **No Enhancement**: Don't add testing, error handling, or other features unless mentioned
- **Original Language**: Use the terminology and descriptions from the source material
- **Stated Dependencies**: Only mention connections explicitly described in the content
- **As-Written Scope**: Preserve the complexity level described in the original content
- **Direct Translation**: Convert markdown content to GitHub issues without interpretation

🎯 EDGE CASE HANDLING:

- **Minimal Content**: If markdown has few details, create simple issues that match the brief descriptions
- **Vague Descriptions**: Use the exact vague language provided - don't add specificity not in the source
- **Mixed Content Types**: Only separate work types if they're actually separated in the original content
- **Incomplete Information**: Create issues with the incomplete information as-is, don't fill in gaps
- **Brief Mentions**: If something is mentioned briefly, create a correspondingly brief issue

⚠️ **REMEMBER**: Your job is to organize and structure the existing content, not to enhance or complete it.

MARKDOWN CONTENT TO ANALYZE:
{markdown_content}

Analyze this {content_type.replace('_', ' ')} content thoroughly and create a professional GitHub project structure following ALL the guidelines above. Ensure your response is valid JSON with comprehensive reasoning and a well-organized milestone structure."""
    
    # Add contextual notes based on content analysis
    return validate_and_enhance_prompt(prompt, markdown_content)

def call_deepseek_api(
    prompt: str,
    model: str = "deepseek-chat",
    temperature: float = 0.3,
    max_tokens: int = 4000
) -> Dict[str, Any]:
    """
    Make a call to the DeepSeek API.
    
    Args:
        prompt: The prompt to send to DeepSeek
        model: The model to use (default: deepseek-chat)
        temperature: Temperature for response generation
        max_tokens: Maximum tokens in response
        
    Returns:
        API response data
        
    Raises:
        DeepSeekError: If the API call fails
    """
    validate_deepseek_config()
    
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": False
    }
    
    try:
        response = requests.post(
            f"{DEEPSEEK_BASE_URL}/chat/completions",
            headers=headers,
            json=payload,
            timeout=120  # Increased timeout for better reliability
        )
        
        if response.status_code != 200:
            raise DeepSeekError(
                f"DeepSeek API request failed",
                status_code=response.status_code,
                response_text=response.text
            )
        
        return response.json()
    
    except requests.RequestException as e:
        raise DeepSeekError(f"Request error: {str(e)}")

def parse_deepseek_response(response_data: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
    """
    Parse the DeepSeek API response and extract reasoning and structure.
    
    Args:
        response_data: Raw response from DeepSeek API
        
    Returns:
        Tuple of (reasoning, structure)
        
    Raises:
        DeepSeekError: If response format is invalid
    """
    try:
        # Extract the content from the response
        if "choices" not in response_data or not response_data["choices"]:
            raise DeepSeekError("Invalid response format: no choices found")
        
        content = response_data["choices"][0]["message"]["content"]
        
        # Parse the JSON content
        try:
            parsed_content = json.loads(content)
        except json.JSONDecodeError as e:
            # Try to extract JSON from markdown code blocks if present
            import re
            json_match = re.search(r'```(?:json)?\s*(\{.*\})\s*```', content, re.DOTALL)
            if json_match:
                parsed_content = json.loads(json_match.group(1))
            else:
                raise DeepSeekError(f"Failed to parse JSON response: {str(e)}")
        
        # Validate required fields
        if "reasoning" not in parsed_content:
            raise DeepSeekError("Response missing 'reasoning' field")
        if "structure" not in parsed_content:
            raise DeepSeekError("Response missing 'structure' field")
        
        return parsed_content["reasoning"], parsed_content["structure"]
    
    except Exception as e:
        if isinstance(e, DeepSeekError):
            raise
        raise DeepSeekError(f"Error parsing DeepSeek response: {str(e)}")

def ai_parse_markdown(markdown_content: str) -> Tuple[str, Dict[str, Any]]:
    """
    Use DeepSeek AI to parse markdown content into GitHub milestones and issues.
    
    Args:
        markdown_content: The markdown content to analyze
        
    Returns:
        Tuple of (reasoning, structured_data)
        
    Raises:
        DeepSeekError: If the AI parsing fails
    """
    if not markdown_content or not markdown_content.strip():
        raise DeepSeekError("Empty markdown content provided")
    
    # Create the prompt
    prompt = create_master_prompt(markdown_content)
    
    # Call DeepSeek API
    response_data = call_deepseek_api(prompt)
    
    # Parse and return the response
    return parse_deepseek_response(response_data)

def validate_ai_structure(structure: Dict[str, Any]) -> List[str]:
    """
    Validate the AI-generated structure for completeness and correctness.
    
    Args:
        structure: The structure returned by AI
        
    Returns:
        List of validation errors (empty if valid)
    """
    errors = []
    
    if not isinstance(structure, dict):
        errors.append("Structure must be a dictionary")
        return errors
    
    if not structure:
        errors.append("Structure is empty")
        return errors
    
    for milestone_name, milestone_data in structure.items():
        if not isinstance(milestone_data, dict):
            errors.append(f"Milestone '{milestone_name}' data must be a dictionary")
            continue
        
        # Check required fields
        required_fields = ["description", "issues"]
        for field in required_fields:
            if field not in milestone_data:
                errors.append(f"Milestone '{milestone_name}' missing required field: {field}")
        
        # Validate issues
        if "issues" in milestone_data:
            if not isinstance(milestone_data["issues"], list):
                errors.append(f"Milestone '{milestone_name}' issues must be a list")
            else:
                for i, issue in enumerate(milestone_data["issues"]):
                    if not isinstance(issue, dict):
                        errors.append(f"Milestone '{milestone_name}', issue {i+1} must be a dictionary")
                        continue
                    
                    # Check required issue fields
                    if "title" not in issue or not issue["title"]:
                        errors.append(f"Milestone '{milestone_name}', issue {i+1} missing title")
                    if "body" not in issue:
                        errors.append(f"Milestone '{milestone_name}', issue {i+1} missing body")
                    if "labels" not in issue:
                        errors.append(f"Milestone '{milestone_name}', issue {i+1} missing labels")
                    if "assignees" not in issue:
                        errors.append(f"Milestone '{milestone_name}', issue {i+1} missing assignees")
    
    return errors

def detect_content_type(markdown_content: str) -> str:
    """
    Analyze markdown content to determine its type for adaptive prompt generation.
    
    Args:
        markdown_content: The markdown content to analyze
        
    Returns:
        Content type string for prompt customization
    """
    content_lower = markdown_content.lower()
    
    # Technical project indicators
    technical_keywords = [
        'api', 'database', 'frontend', 'backend', 'deployment', 'testing',
        'architecture', 'framework', 'library', 'code', 'implementation',
        'docker', 'kubernetes', 'ci/cd', 'repository', 'git', 'npm', 'pip'
    ]
    
    # Business requirements indicators  
    business_keywords = [
        'requirements', 'user story', 'acceptance criteria', 'business logic',
        'workflow', 'process', 'stakeholder', 'customer', 'revenue', 'roi',
        'compliance', 'regulation', 'policy', 'strategy', 'objective'
    ]
    
    # Research/analysis indicators
    research_keywords = [
        'analysis', 'research', 'investigation', 'study', 'evaluation',
        'comparison', 'assessment', 'findings', 'methodology', 'data',
        'metrics', 'kpi', 'benchmark', 'report', 'insights'
    ]
    
    # Planning/roadmap indicators
    planning_keywords = [
        'roadmap', 'milestone', 'timeline', 'phase', 'sprint', 'release',
        'planning', 'schedule', 'deliverable', 'goal', 'initiative',
        'quarter', 'q1', 'q2', 'q3', 'q4', 'fy', 'budget'
    ]
    
    # Count keyword matches
    technical_score = sum(1 for keyword in technical_keywords if keyword in content_lower)
    business_score = sum(1 for keyword in business_keywords if keyword in content_lower)
    research_score = sum(1 for keyword in research_keywords if keyword in content_lower)
    planning_score = sum(1 for keyword in planning_keywords if keyword in content_lower)
    
    # Determine content type based on highest score
    scores = {
        'technical_project': technical_score,
        'business_requirements': business_score,
        'research_analysis': research_score,
        'planning_roadmap': planning_score
    }
    
    max_score = max(scores.values())
    
    # If scores are close or low, classify as mixed content
    if max_score < 3 or list(scores.values()).count(max_score) > 1:
        return 'mixed_content'
    
    # Return the content type with highest score
    return max(scores, key=scores.get)

def get_content_specific_instructions(content_type: str) -> str:
    """
    Get content-specific analysis instructions.
    
    Args:
        content_type: The detected content type
        
    Returns:
        Formatted instructions string
    """
    instructions = {
        "technical_project": """
🎯 TECHNICAL PROJECT ANALYSIS:
This appears to be a technical project document. Focus on:
- Code architecture and implementation tasks
- Development workflow and tooling setup
- Testing and quality assurance requirements
- Deployment and infrastructure needs
- Documentation and knowledge sharing

Create issues that reflect technical implementation phases with appropriate technical labels.
""",
        
        "business_requirements": """
🎯 BUSINESS REQUIREMENTS ANALYSIS:
This appears to be a business requirements document. Focus on:
- Feature specifications and user stories
- Business logic and workflow requirements
- Integration and data flow needs
- User experience and interface requirements
- Acceptance criteria and validation rules

Create issues that translate business needs into technical implementation tasks.
""",
        
        "research_analysis": """
🎯 RESEARCH/ANALYSIS DOCUMENT:
This appears to be a research or analysis document. Focus on:
- Investigation and discovery tasks
- Data analysis and reporting requirements
- Tool evaluation and comparison tasks
- Documentation and knowledge capture
- Recommendation implementation

Create issues that structure research activities and their outcomes into actionable tasks.
""",
        
        "planning_roadmap": """
🎯 PLANNING/ROADMAP DOCUMENT:
This appears to be a planning or roadmap document. Focus on:
- Strategic initiative breakdown
- Phase-based implementation planning
- Resource allocation and timeline considerations
- Milestone and deliverable definitions
- Risk assessment and mitigation planning

Create issues that reflect strategic execution with clear phases and dependencies.
""",
        
        "mixed_content": """
🎯 MIXED CONTENT ANALYSIS:
This document contains various types of content. Focus on:
- Identifying different work streams and their requirements
- Balancing technical and business objectives
- Creating logical groupings and dependencies
- Ensuring comprehensive coverage of all identified areas
- Maintaining coherent project flow

Create issues that cover all aspects while maintaining logical organization.
"""
    }
    
    return instructions.get(content_type, instructions["mixed_content"])

def get_enhanced_labels_for_content_type(content_type: str) -> str:
    """
    Get enhanced label definitions based on content type.
    
    Args:
        content_type: The detected content type
        
    Returns:
        Formatted label definitions string
    """
    
    base_labels = """
📋 ENHANCED LABEL SYSTEM:

**Core Functional Labels:**
- 🧪 `testing-qa` (Testing & Quality Assurance)
- 📚 `documentation` (Documentation & Guides)
- 🔒 `security` (Security-related tasks)
- 🚀 `deployment` (Deployment and DevOps)
"""
    
    content_specific_labels = {
        'technical_project': """
**Technical Implementation Labels:**
- 🗄️ `database` (Database design and implementation)
- ⚡ `code-quality` (Code optimization and refactoring)
- 🛠️ `tech-stack` (Technology evaluation and setup)
- 🎨 `frontend` (Frontend/UI development)
- 🏗️ `backend` (Backend/API development)
- 🔗 `integration` (System integration tasks)
- 🧰 `tooling` (Development tools and automation)
- 📦 `dependencies` (Library and package management)
""",
        
        'business_requirements': """
**Business & Feature Labels:**
- 🔍 `feature-analysis` (Feature specification and analysis)
- 👥 `user-experience` (UX/UI and user journey tasks)
- 📊 `analytics` (Metrics and tracking implementation)
- 🔄 `workflow` (Business process implementation)
- 📋 `requirements` (Requirements gathering and validation)
- 🎯 `user-story` (User story implementation)
- 💼 `business-logic` (Core business rule implementation)
""",
        
        'research_analysis': """
**Research & Analysis Labels:**
- 🔬 `research` (Investigation and discovery tasks)
- 📈 `data-analysis` (Data processing and analysis)
- 🔍 `evaluation` (Tool and solution evaluation)
- 📊 `reporting` (Report generation and presentation)
- 🧪 `experimentation` (A/B testing and experiments)
- 📋 `findings` (Research outcome documentation)
- 🎯 `recommendations` (Action item implementation)
""",
        
        'planning_roadmap': """
**Planning & Strategy Labels:**
- 🗺️ `roadmap` (Strategic planning and roadmap items)
- 🎯 `milestone` (Major milestone and deliverable tasks)
- 📅 `timeline` (Schedule and timing coordination)
- 🔄 `phase` (Project phase management)
- 📊 `resource-planning` (Resource allocation and management)
- 🎪 `stakeholder` (Stakeholder communication and coordination)
- 🎯 `objective` (Goal setting and tracking)
""",
        
        'mixed_content': """
**Comprehensive Label Set:**
- 🗄️ `database-migration` (Database & Migration Strategy)
- ⚡ `code-quality` (Code Quality & Optimization)
- 🔍 `feature-analysis` (Core Feature Analysis)
- 🛠️ `tech-stack` (Technology Stack Assessment)
- 🎨 `frontend` (Frontend/UI related tasks)
- 🏗️ `backend` (Backend/API related tasks)
- 🔗 `integration` (System integration tasks)
- 📊 `analytics` (Data and metrics tasks)
"""
    }
    
    priority_labels = """
**Priority & Type Labels:**
- 🔴 `high-priority` (Critical/urgent tasks)
- 🟡 `medium-priority` (Important but not urgent)  
- 🟢 `low-priority` (Nice-to-have features)
- 🐛 `bug` (Bug fixes and issues)
- ✨ `enhancement` (New features and improvements)
- 🔧 `maintenance` (Code maintenance and refactoring)
- 📋 `task` (General implementation tasks)
- 🎯 `epic` (Large feature sets requiring multiple issues)
"""
    
    return base_labels + content_specific_labels.get(content_type, content_specific_labels['mixed_content']) + priority_labels

def get_content_examples(content_type: str) -> str:
    """
    Get content-specific examples for the prompt.
    
    Args:
        content_type: The detected content type
        
    Returns:
        Formatted examples string
    """
    
    examples = {
        'technical_project': """
🎯 **TECHNICAL PROJECT EXAMPLE (CLAUDE-OPTIMIZED):**

**Perfect Size Issue for Claude Computer Use:**
```
Title: "[Backend] Implement user authentication API with session management"
Body: "Create complete user authentication system with API endpoints and session management - sized for single Claude development session.

🎯 **Scope**: 4-6 hours of focused development (Claude-optimal)
📋 **Feature Requirements**: 
- User registration with email/password
- User login with session management
- Secure logout functionality
- Token refresh mechanism
- Password reset capability
- Rate limiting for security

🏗️ **Complete Feature Specification:**

Authentication Flow:
- Registration: Accept email/password, validate format, create user account
- Login: Verify credentials, create session, return authentication token
- Logout: Invalidate session/token, clear client-side auth data
- Refresh: Extend session without requiring re-login
- Reset: Send reset email, validate reset token, update password

Security Requirements:
- Passwords must be securely hashed (never stored in plain text)
- Rate limiting: Maximum 5 login attempts per minute per IP
- Sessions/tokens should expire appropriately (15min active, 7day refresh)
- All endpoints should validate input and return proper error messages
- Reset tokens should be single-use and expire within 1 hour

API Endpoints Needed:
- POST /api/auth/register (email, password, confirmPassword)
- POST /api/auth/login (email, password)
- POST /api/auth/logout (authenticated)
- POST /api/auth/refresh (refresh token)
- POST /api/auth/forgot-password (email)
- POST /api/auth/reset-password (token, newPassword)
- GET /api/auth/me (get current user info)

Data Requirements:
- User storage: email, hashed password, created date, last login
- Session storage: user ID, token, expiration, refresh token
- Reset tokens: user ID, token, expiration time

Error Handling:
- Invalid credentials: Return 401 with generic "Invalid email or password"
- Rate limiting: Return 429 with "Too many attempts, try again later"
- Invalid input: Return 400 with specific field validation errors
- Server errors: Return 500 with safe error message (no stack traces)

Acceptance Criteria:
✅ Users can register with valid email/password combinations
✅ Users can login with correct credentials
✅ Invalid login attempts are properly rejected
✅ Rate limiting blocks excessive requests
✅ Sessions expire and can be refreshed
✅ Password reset flow works end-to-end
✅ All error cases return appropriate messages
✅ Security best practices are followed

Note: Claude should research and choose appropriate technologies, frameworks, and implementation patterns based on the project context."

Labels: ["backend", "enhancement", "high-priority", "security"]
```

❌ **AVOID - Too Small (Micro-task):**
```
Title: "Add email validation to registration"
Body: "Add email format validation to the registration endpoint"
```
❌ **AVOID - Too Large (Multi-session):**
```
Title: "Build complete user management system"
Body: "Implement authentication, authorization, user profiles, admin panel, permissions..."
```
❌ **AVOID - Too Specific (Assumes tech stack):**
```
Title: "Add JWT authentication to Express.js routes"
Body: "Implement JWT middleware using jsonwebtoken library with bcrypt password hashing..."
```
""",
        'mixed_content': """
🎯 **MIXED CONTENT EXAMPLE (CONTENT-FAITHFUL):**

**Example Markdown Input:**
```markdown
# User Dashboard Project

Create a dashboard for users to view their information.

## Profile Section
- Display user name and email
- Show profile picture

## Activity Timeline
- Show recent user activities
- Display timestamps

## Basic Charts
- Create simple charts showing user data
```

**Correct DeepSeek Output:**
```
Title: "[Frontend] Build user dashboard with profile and activity sections"
Body: "Create a dashboard for users to view their information as specified.

Components to build (from markdown requirements):
- Profile section displaying user name, email, and profile picture
- Activity timeline showing recent user activities with timestamps
- Basic charts showing user data

This implements exactly the dashboard features described in the requirements."

Labels: ["frontend", "enhancement"]
```

❌ **WRONG - Adding features not mentioned:**
```
Title: "[Frontend] Build comprehensive analytics dashboard with real-time features"
Body: "Create advanced user dashboard with:
- Real-time data updates every 30 seconds
- Interactive charts with drill-down capabilities
- Data export functionality to CSV/PDF
- Date range filtering (7d, 30d, 90d, custom)
- Responsive design for mobile/tablet/desktop
- Dark/light theme support
- Search and filter functionality
- Performance metrics and KPIs
- User preference settings"
```
⚠️ **Problem**: Added real-time updates, export, filtering, themes, etc. - none mentioned in original content!

✅ **CORRECT APPROACH:**
- Only create what's explicitly mentioned
- Use the same terminology as the source
- Keep the scope exactly as described
- Don't enhance or "improve" the requirements
"""
    }
    
    return examples.get(content_type, examples['mixed_content'])

def validate_and_enhance_prompt(prompt: str, markdown_content: str) -> str:
    """
    Validate and enhance the generated prompt with additional context.
    
    Args:
        prompt: Generated prompt string
        markdown_content: Original markdown content
        
    Returns:
        Enhanced and validated prompt
    """
    
    # Add content length context
    content_length = len(markdown_content)
    complexity_note = ""
    
    if content_length < 500:
        complexity_note = "\n⚠️ NOTE: This is a short document. Focus on extracting maximum value and creating comprehensive issues even from limited content."
    elif content_length > 5000:
        complexity_note = "\n⚠️ NOTE: This is a long document. Focus on identifying major themes and avoiding over-granular issue creation."
    
    # Add content structure analysis
    header_count = len([line for line in markdown_content.split('\n') if line.strip().startswith('#')])
    if header_count > 10:
        complexity_note += "\n📋 STRUCTURE NOTE: This document has many headers. Use them to guide logical issue grouping and categorization."
    
    # Add estimated scope guidance
    word_count = len(markdown_content.split())
    if word_count > 1000:
        complexity_note += f"\n📊 SCOPE GUIDANCE: With {word_count} words, aim for 5-15 well-structured issues optimized for Claude's context window and Computer Use capabilities. Each issue should represent 2-8 hours of focused development work."
    
    return prompt + complexity_note

def test_deepseek_connection() -> Tuple[bool, str]:
    """
    Test the connection to DeepSeek API.
    
    Returns:
        Tuple of (success, message)
    """
    try:
        validate_deepseek_config()
        
        # Make a simple test call
        test_prompt = "Respond with just 'OK' if you can read this message."
        response = call_deepseek_api(test_prompt, max_tokens=10)
        
        if "choices" in response and response["choices"]:
            return True, "DeepSeek API connection successful"
        else:
            return False, "Unexpected response format from DeepSeek API"
    
    except DeepSeekError as e:
        return False, str(e)
    except Exception as e:
        return False, f"Unexpected error: {str(e)}"
