import pytest
import os
from unittest.mock import patch, mock_open
from get_version import get_latest_tag_with_module, process

def get_version_file_path(filename):
    return os.path.join(os.path.dirname(__file__), "test_resources", filename)

# Test with semver version file
@patch("get_version.get_tags")
@patch("get_version.set_output")
def test_simple_module_tag(mock_set_output, mock_get_tags):
    # Setup
    mock_get_tags.return_value = ["node-1.0.0", "node-1.0.1"]
    mock_set_output.return_value = None
    version_file = get_version_file_path("version_semver.txt")  # Contains "1.0.0"
    
    # Test
    result = get_latest_tag_with_module(
        module="node",
        version_file=version_file
    )
    
    # The result should be node-1.0.2 because:
    # 1. Latest tag is node-1.0.1
    # 2. Base version in version_semver.txt is 1.0.0
    # 3. Since latest tag > base version, increment patch number
    assert result == "node-1.0.2"

# Test with major.minor version file
@patch("get_version.get_tags")
@patch("get_version.set_output")
def test_hyphenated_module_tag(mock_set_output, mock_get_tags):
    """Test module tags with hyphens using proper version format"""
    # Setup
    mock_get_tags.return_value = ["my-node-1.0.0", "my-node-1.0.1"]
    mock_set_output.return_value = None
    
    # Create a mock version file with proper semver format
    mock_version_content = "1.0.0"
    
    # Use context manager to mock the file open operation
    with patch("builtins.open", mock_open(read_data=mock_version_content)):
        result = get_latest_tag_with_module(
            module="my-node",
            version_file="version.txt"
        )
        
        # Should increment patch version since we're using semver format
        # Latest tag is 1.0.1, so next should be 1.0.2
        assert result == "my-node-1.0.2"

# Add a test for major.minor format explicitly
@patch("get_version.get_tags")
@patch("get_version.set_output")
def test_hyphenated_module_tag_major_minor(mock_set_output, mock_get_tags):
    """Test module tags with major.minor version format"""
    # Setup
    mock_get_tags.return_value = ["my-node-1.0", "my-node-1.1"]
    mock_set_output.return_value = None
    
    # Create a mock version file with major.minor format
    mock_version_content = "1.0"
    
    # Use context manager to mock the file open operation
    with patch("builtins.open", mock_open(read_data=mock_version_content)):
        result = get_latest_tag_with_module(
            module="my-node",
            version_file="version.txt"
        )
        
        # Should increment minor version since we're using major.minor format
        assert result == "my-node-1.2"

# Test version comparison logic
@patch("get_version.get_tags")
@patch("get_version.set_output")
def test_version_comparison(mock_set_output, mock_get_tags):
    # Setup
    mock_get_tags.return_value = ["node-1.0.1"]
    mock_set_output.return_value = None
    version_file = get_version_file_path("version_semver.txt")  # Contains "1.0.0"
    
    # Test
    result = get_latest_tag_with_module(
        module="node",
        version_file=version_file
    )
    
    # The result should be node-1.0.2 because:
    # 1. Current tag (1.0.1) is greater than base version (1.0.0)
    # 2. Therefore, increment the patch version of current tag
    assert result == "node-1.0.2"

# Test base version precedence
@patch("get_version.get_tags")
@patch("get_version.set_output")
def test_base_version_precedence(mock_set_output, mock_get_tags):
    # Setup
    mock_get_tags.return_value = ["node-0.9.9"]
    mock_set_output.return_value = None
    version_file = get_version_file_path("version_semver.txt")  # Contains "1.0.0"
    
    # Test
    result = get_latest_tag_with_module(
        module="node",
        version_file=version_file
    )
    
    # The result should be node-1.0.0 because:
    # 1. Current tag (0.9.9) is less than base version (1.0.0)
    # 2. Therefore, use the base version from version file
    assert result == "node-1.0.0" 