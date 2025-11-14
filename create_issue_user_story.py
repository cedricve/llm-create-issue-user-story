#!/usr/bin/env python3
import sys
import requests
import argparse
import os
from openai import AzureOpenAI, OpenAI

SAMPLE_PROMPT = """
Generate a detailed user story for a software development task with the following structure:

# Title
[A concise, descriptive title for the user story]

## User Story
As a [type of user], I want [goal] so that [benefit].

## Acceptance Criteria
- List specific, testable criteria that define when this story is complete
- Each criterion should be clear and measurable
- Include at least 3-5 acceptance criteria

## Technical Details
- List technical considerations or implementation notes
- Include any dependencies or prerequisites
- Mention potential challenges or risks

## Testing Strategy
- Describe how this feature should be tested
- Include different types of testing (unit, integration, etc.)

## Definition of Done
- Checklist of items that must be completed for this story to be considered done
"""

GOOD_SAMPLE_RESPONSE = """
# Implement User Authentication System

## User Story
As a developer, I want to implement user authentication so that users can securely access their accounts.

## Acceptance Criteria
- Users can register with email and password
- Users can log in with their credentials
- Users can log out from the application
- Session tokens expire after 24 hours
- Failed login attempts are limited to 5 per hour

## Technical Details
- Use JWT tokens for authentication
- Hash passwords using bcrypt
- Store user credentials in the database
- Implement rate limiting for login attempts
- Add middleware for protected routes
- Dependencies: bcrypt, jsonwebtoken libraries

## Testing Strategy
- Unit tests for authentication functions
- Integration tests for login/logout flow
- Security testing for password hashing
- Load testing for rate limiting
- Edge case testing (invalid credentials, expired tokens)

## Definition of Done
- [ ] Code is written and reviewed
- [ ] Unit tests pass with >80% coverage
- [ ] Integration tests pass
- [ ] Security scan shows no vulnerabilities
- [ ] Documentation is updated
- [ ] Feature is deployed to staging environment
"""

COMPLETION_PROMPT = """
Based on the provided information, generate a comprehensive user story following the structure above.
"""


def extract_title_from_response(response_text):
    """
    Extract the title from the LLM response.
    Expected format: # Title\n or Title:\n at the beginning of the response.
    Falls back to first line if no markdown header is found.
    """
    lines = response_text.strip().split('\n')
    
    for line in lines:
        # Check for markdown header (# Title)
        if line.strip().startswith('# '):
            return line.strip()[2:].strip()
        # Check for "Title:" format
        if line.lower().startswith('title:'):
            return line.split(':', 1)[1].strip()
    
    # Fallback: use the first non-empty line as title
    for line in lines:
        if line.strip():
            return line.strip().lstrip('#').strip()
    
    return "User Story"  # Ultimate fallback


def extract_body_from_response(response_text):
    """
    Extract the body (everything except the title) from the LLM response.
    Removes the title line from the response.
    """
    lines = response_text.strip().split('\n')
    
    # Find and skip the title line
    for i, line in enumerate(lines):
        if line.strip().startswith('# ') or line.lower().startswith('title:'):
            # Return everything after the title line
            return '\n'.join(lines[i+1:]).strip()
    
    # If no title found, return the whole response
    return response_text.strip()


def main():
    parser = argparse.ArgumentParser(
        description="Use ChatGPT to generate a user story for a GitHub issue."
    )
    parser.add_argument(
        "--github-api-url", type=str, required=True, help="The GitHub API URL"
    )
    parser.add_argument(
        "--github-repository", type=str, required=True, help="The GitHub repository"
    )
    parser.add_argument(
        "--github-token",
        type=str,
        required=True,
        help="The GitHub token",
    )
    parser.add_argument(
        "--openai-api-key",
        type=str,
        required=False,
        default="",
        help="The OpenAI API key",
    )
    parser.add_argument(
        "--azure-openai-api-key",
        type=str,
        required=False,
        default="",
        help="The Azure OpenAI API key",
    )
    parser.add_argument(
        "--azure-openai-endpoint",
        type=str,
        required=False,
        default="",
        help="The Azure OpenAI endpoint",
    )
    parser.add_argument(
        "--azure-openai-version",
        type=str,
        required=False,
        default="",
        help="The Azure OpenAI API version",
    )
    parser.add_argument(
        "--issue-title",
        type=str,
        required=True,
        help="The title of the GitHub issue",
    )
    parser.add_argument(
        "--issue-description",
        type=str,
        required=True,
        help="Brief description of the feature or user story",
    )
    parser.add_argument(
        "--complexity",
        type=str,
        required=False,
        default="Medium",
        help="Complexity level of the user story",
    )
    parser.add_argument(
        "--duration",
        type=str,
        required=False,
        default="1 week",
        help="Estimated duration for the user story",
    )
    parser.add_argument(
        "--labels",
        type=str,
        required=False,
        default="",
        help="Comma-separated list of labels to add to the issue",
    )
    parser.add_argument(
        "--assignees",
        type=str,
        required=False,
        default="",
        help="Comma-separated list of assignees for the issue",
    )

    args = parser.parse_args()

    github_api_url = args.github_api_url
    repo = args.github_repository
    github_token = args.github_token
    openai_api_key = args.openai_api_key
    azure_openai_api_key = args.azure_openai_api_key
    azure_openai_endpoint = args.azure_openai_endpoint
    azure_openai_version = args.azure_openai_version
    issue_title = args.issue_title
    issue_description = args.issue_description
    complexity = args.complexity
    duration = args.duration
    labels = args.labels
    assignees = args.assignees

    open_ai_model = os.environ.get("INPUT_OPENAI_MODEL", "gpt-4o-mini")
    max_prompt_tokens = int(os.environ.get("INPUT_MAX_TOKENS", "2000"))
    model_temperature = float(os.environ.get("INPUT_TEMPERATURE", "0.7"))

    authorization_header = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"token {github_token}",
    }

    # Prepare the completion prompt with the user-provided information
    user_prompt = f"""
{COMPLETION_PROMPT}

Title: {issue_title}
Description: {issue_description}
Complexity: {complexity}
Estimated Duration: {duration}

Please generate a complete user story that addresses this requirement.
"""

    print(f"Generating user story with LLM...")
    print(f"Issue Title: {issue_title}")
    print(f"Description: {issue_description}")
    print(f"Complexity: {complexity}")
    print(f"Duration: {duration}")

    generated_user_story = ""
    
    # Use OpenAI or Azure OpenAI based on which API key is provided
    if openai_api_key:
        print("Using OpenAI API...")
        openai_client = OpenAI(api_key=openai_api_key)
        openai_response = openai_client.chat.completions.create(
            model=open_ai_model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant who writes detailed user stories for software development.",
                },
                {"role": "user", "content": SAMPLE_PROMPT},
                {"role": "assistant", "content": GOOD_SAMPLE_RESPONSE},
                {"role": "user", "content": user_prompt},
            ],
            temperature=model_temperature,
            max_tokens=max_prompt_tokens,
        )
        generated_user_story = openai_response.choices[0].message.content

    elif azure_openai_api_key:
        print("Using Azure OpenAI API...")
        azure_openai_client = AzureOpenAI(
            api_key=azure_openai_api_key,
            azure_endpoint=azure_openai_endpoint,
            api_version=azure_openai_version
        )
        azure_openai_response = azure_openai_client.chat.completions.create(
            model=open_ai_model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant who writes detailed user stories for software development.",
                },
                {"role": "user", "content": SAMPLE_PROMPT},
                {"role": "assistant", "content": GOOD_SAMPLE_RESPONSE},
                {"role": "user", "content": user_prompt},
            ],
            temperature=model_temperature,
            max_tokens=max_prompt_tokens,
        )
        generated_user_story = azure_openai_response.choices[0].message.content
    else:
        print("Error: Either openai_api_key or azure_openai_api_key must be provided")
        return 1

    print(f"Generated user story:\n{generated_user_story}")

    # Extract title and body from the generated response
    extracted_title = extract_title_from_response(generated_user_story)
    extracted_body = extract_body_from_response(generated_user_story)
    
    print(f"\nExtracted title: {extracted_title}")
    print(f"Using LLM-generated title instead of user-provided title: '{issue_title}'")

    # Create the GitHub issue
    issue_url = f"{github_api_url}/repos/{repo}/issues"
    issue_data = {
        "title": extracted_title,
        "body": extracted_body,
    }

    # Add labels if provided
    if labels:
        label_list = [label.strip() for label in labels.split(",") if label.strip()]
        if label_list:
            issue_data["labels"] = label_list

    # Add assignees if provided
    if assignees:
        assignee_list = [assignee.strip() for assignee in assignees.split(",") if assignee.strip()]
        if assignee_list:
            issue_data["assignees"] = assignee_list

    print(f"Creating GitHub issue...")
    issue_response = requests.post(issue_url, headers=authorization_header, json=issue_data)
    
    if issue_response.status_code != 201:
        print(f"Failed to create issue: {issue_response.status_code}, {issue_response.text}")
        return 1
    
    issue_number = issue_response.json()["number"]
    issue_html_url = issue_response.json()["html_url"]
    print(f"GitHub issue created successfully: {issue_html_url}")
    print(f"Issue number: {issue_number}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
