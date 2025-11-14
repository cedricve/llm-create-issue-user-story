#!/usr/bin/env python3
"""Test suite for title extraction from LLM responses."""

from create_issue_user_story import extract_title_from_response, extract_body_from_response


def test_standard_markdown_header():
    """Test extraction of a standard markdown header."""
    response = """# Implement User Authentication System

## User Story
As a developer, I want to implement user authentication so that users can securely access their accounts."""
    
    title = extract_title_from_response(response)
    assert title == "Implement User Authentication System", f"Expected 'Implement User Authentication System', got '{title}'"
    print("✓ Test passed: Standard markdown header")


def test_title_with_prefix():
    """Test extraction when title is prefixed with 'Title:'."""
    response = """Title: Add New Feature

## User Story
As a user, I want to add a new feature."""
    
    title = extract_title_from_response(response)
    assert title == "Add New Feature", f"Expected 'Add New Feature', got '{title}'"
    print("✓ Test passed: Title with 'Title:' prefix")


def test_generic_title_placeholder():
    """Test that generic 'Title' placeholder is rejected."""
    response = """# Title

## User Story
As a developer, I want to create a feature."""
    
    title = extract_title_from_response(response)
    # Should NOT return just "Title" - should look for alternative or use fallback
    assert title != "Title", f"Should not extract generic 'Title' placeholder, got '{title}'"
    print(f"✓ Test passed: Generic 'Title' placeholder rejected (got '{title}')")


def test_title_in_brackets():
    """Test extraction when title is in brackets (template format)."""
    response = """# [A concise, descriptive title for the user story]

## User Story
As a developer, I want to create a feature."""
    
    title = extract_title_from_response(response)
    # Should NOT return text in brackets - should look for alternative or use fallback
    assert not title.startswith('['), f"Should not extract bracketed template text, got '{title}'"
    print(f"✓ Test passed: Bracketed template text rejected (got '{title}')")


def test_whitespace_handling():
    """Test that whitespace is properly handled."""
    response = """#    My Feature Title   

## User Story
As a developer..."""
    
    title = extract_title_from_response(response)
    assert title == "My Feature Title", f"Expected 'My Feature Title', got '{title}'"
    print("✓ Test passed: Whitespace handling")


def test_no_clear_title_uses_fallback():
    """Test fallback when no clear title is found."""
    response = """## User Story
As a developer, I want to create a feature.

## Acceptance Criteria
- Feature works correctly"""
    
    title = extract_title_from_response(response)
    # Should use some reasonable fallback
    assert title and len(title) > 0, f"Should have a fallback title, got '{title}'"
    print(f"✓ Test passed: Fallback used when no clear title (got '{title}')")


def test_body_extraction():
    """Test that body extraction removes the title."""
    response = """# Implement User Authentication System

## User Story
As a developer, I want to implement user authentication.

## Acceptance Criteria
- Users can register
- Users can login"""
    
    body = extract_body_from_response(response)
    assert not body.startswith("# Implement"), f"Body should not start with title"
    assert "## User Story" in body, f"Body should contain user story section"
    print("✓ Test passed: Body extraction removes title")


def test_multiline_title_edge_case():
    """Test that we don't extract multiline content as title."""
    response = """# Create a comprehensive
authentication system with JWT

## User Story
As a developer..."""
    
    title = extract_title_from_response(response)
    # Should only get first line
    assert "authentication system" not in title or "\n" not in title, f"Title should not be multiline, got '{title}'"
    print(f"✓ Test passed: Multiline title edge case (got '{title}')")


def test_real_world_example():
    """Test with a real-world-like LLM response."""
    response = """# Implement Dark Mode Toggle Feature

## User Story
As a user, I want to toggle between light and dark modes so that I can use the application comfortably in different lighting conditions.

## Acceptance Criteria
- User can click a toggle button to switch between light and dark modes
- User preference is persisted across sessions
- All UI components properly support both themes
- Toggle transition is smooth and visually appealing
- Theme choice is accessible via keyboard navigation

## Technical Details
- Use CSS variables for theme colors
- Store user preference in localStorage
- Implement theme context provider in React
- Ensure proper contrast ratios for accessibility
- Dependencies: None (vanilla CSS)

## Testing Strategy
- Unit tests for theme toggle logic
- Visual regression tests for both themes
- Accessibility testing with screen readers
- Cross-browser compatibility testing
- Local storage persistence testing

## Definition of Done
- [ ] Code is written and reviewed
- [ ] Unit tests pass with >80% coverage
- [ ] Visual regression tests pass
- [ ] Accessibility audit passes
- [ ] Documentation is updated
- [ ] Feature is deployed to staging environment"""
    
    title = extract_title_from_response(response)
    assert title == "Implement Dark Mode Toggle Feature", f"Expected 'Implement Dark Mode Toggle Feature', got '{title}'"
    print("✓ Test passed: Real-world example")


def run_all_tests():
    """Run all test cases."""
    print("Running title extraction tests...\n")
    
    test_standard_markdown_header()
    test_title_with_prefix()
    test_generic_title_placeholder()
    test_title_in_brackets()
    test_whitespace_handling()
    test_no_clear_title_uses_fallback()
    test_body_extraction()
    test_multiline_title_edge_case()
    test_real_world_example()
    
    print("\n✅ All tests passed!")


if __name__ == "__main__":
    run_all_tests()
