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

def create_master_prompt(markdown_content: str) -> str:
    """
    Create the master prompt for DeepSeek to analyze markdown and convert to GitHub structure.
    Uses the single milestone + labels approach for better organization.
    
    Args:
        markdown_content: The markdown content to analyze
        
    Returns:
        Formatted prompt for DeepSeek
    """
    return f"""You are an expert project manager and GitHub workflow specialist. Your task is to analyze the provided markdown content and convert it into a well-organized GitHub project structure.

🎯 ORGANIZATION STRATEGY:
Instead of creating multiple separate milestones, you should:
1. Create ONE main milestone that represents the overall project/phase
2. Use LABELS to categorize different work streams within that milestone
3. This makes filtering and project management much easier

📋 STANDARD LABELS TO USE:
- 🧪 testing-qa (Testing & Quality Assurance)
- 🗄️ database-migration (Database & Migration Strategy)
- ⚡ code-quality (Code Quality & Optimization)
- 🔍 feature-analysis (Core Feature Analysis)
- 🛠️ tech-stack (Technology Stack Assessment)
- 📚 documentation (Documentation & Guides)
- 🐛 bug (Bug fixes and issues)
- ✨ enhancement (New features and improvements)
- 🚀 deployment (Deployment and DevOps)
- 🔒 security (Security-related tasks)

OUTPUT FORMAT:
You must respond with a JSON object containing:
1. "reasoning" - Your step-by-step analysis and decision-making process
2. "structure" - The organized milestone and issue structure (SINGLE MILESTONE)

The structure should follow this exact format:
{{
  "reasoning": "Your detailed analysis explaining: 1) How you identified the main project theme for the milestone name, 2) How you categorized different content areas using labels, 3) How you broke down content into actionable issues with appropriate labels",
  "structure": {{
    "[Project Number/ID] Main Project Title": {{
      "description": "Comprehensive description of the entire project scope and objectives",
      "state": "open",
      "due_date": null,
      "issues": [
        {{
          "title": "[Area] Specific actionable task title",
          "body": "Detailed description with context, acceptance criteria, and any technical details",
          "labels": ["testing-qa", "high-priority"],
          "assignees": []
        }},
        {{
          "title": "[Database] Another specific task",
          "body": "Clear description of what needs to be done",
          "labels": ["database-migration", "tech-stack"],
          "assignees": []
        }}
      ]
    }}
  }}
}}

🎯 CRITICAL GUIDELINES:
- Create ONLY ONE milestone that encompasses the entire project
- Use labels to categorize different work streams (testing, database, etc.)
- Prefix issue titles with area indicators like [Testing], [Database], [Code Quality]
- Break content into specific, actionable issues
- Use multiple labels per issue when appropriate (e.g., both "database-migration" and "tech-stack")
- Include priority indicators in labels when evident (high-priority, low-priority)
- Group related tasks into comprehensive issues rather than micro-tasks
- Make milestone description cover the entire project scope

MARKDOWN CONTENT TO ANALYZE:
{markdown_content}

Analyze this content and create ONE well-organized milestone with properly labeled issues in the exact JSON format above."""

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
