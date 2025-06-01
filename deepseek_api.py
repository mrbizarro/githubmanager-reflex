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
    
    Args:
        markdown_content: The markdown content to analyze
        
    Returns:
        Formatted prompt for DeepSeek
    """
    return f"""You are an expert project manager and GitHub workflow specialist. Your task is to analyze the provided markdown content and intelligently convert it into a structured format suitable for GitHub milestones and issues.

ANALYSIS REQUIREMENTS:
1. Identify logical project milestones from the content
2. Extract or create meaningful issues within each milestone
3. Suggest appropriate labels based on content context
4. Recommend assignees if mentioned in the content
5. Provide clear reasoning for your decisions

OUTPUT FORMAT:
You must respond with a JSON object containing:
1. "reasoning" - Your step-by-step analysis and decision-making process
2. "structure" - The organized milestone and issue structure

The structure should follow this exact format:
{{
  "reasoning": "Your detailed analysis of the markdown content, explaining how you identified milestones, issues, and their relationships. Explain your thought process for grouping content, creating issue titles, and suggesting labels.",
  "structure": {{
    "Milestone Name 1": {{
      "description": "Clear description of what this milestone achieves",
      "state": "open",
      "due_date": null,
      "issues": [
        {{
          "title": "Concise, actionable issue title",
          "body": "Detailed description of what needs to be done, including acceptance criteria when possible",
          "labels": ["label1", "label2"],
          "assignees": []
        }}
      ]
    }},
    "Milestone Name 2": {{
      "description": "Another milestone description",
      "state": "open", 
      "due_date": null,
      "issues": [
        {{
          "title": "Another issue title",
          "body": "Issue description with context",
          "labels": ["enhancement", "documentation"],
          "assignees": []
        }}
      ]
    }}
  }}
}}

GUIDELINES:
- Create meaningful milestone names that represent major project phases or goals
- Break down content into actionable, specific issues (not too broad, not too granular)
- Use descriptive issue titles that clearly state what needs to be done
- Include relevant context in issue bodies
- Suggest appropriate labels like: bug, enhancement, documentation, feature, setup, testing, etc.
- Only include assignees if they are explicitly mentioned in the markdown
- Ensure issues are properly distributed across milestones
- If the content is a simple list, consider whether items should be separate issues or combined
- Look for natural groupings and dependencies in the content

MARKDOWN CONTENT TO ANALYZE:
{markdown_content}

Analyze this content and provide your response in the exact JSON format specified above."""

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
