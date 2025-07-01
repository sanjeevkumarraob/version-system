import pytest
import os
from unittest.mock import patch, mock_open
from get_version import get_latest_tag_with_module

def get_resource_path(filename):
    """Helper function to get path to test resource files"""
    return os.path.join(os.path.dirname(__file__), "test_resources", filename)

def read_version_file(filename):
    """Helper function to read test resource files"""
    with open(get_resource_path(filename), 'r') as f:
        return f.read().strip()

@patch.dict(os.environ, {'GITHUB_OUTPUT': 'github_output.txt'})
@patch("get_version.get_tags")
def test_invalid_version_file(mock_get_tags):
    """Test handling of invalid version file"""
    # Setup
    mock_get_tags.return_value = ["test-1.0.0"]  # Provide some tags to avoid no tags error
    
    with pytest.raises(ValueError) as exc_info:
        with patch("builtins.open", mock_open(read_data="invalid version")):
            get_latest_tag_with_module(
                module="test",
                version_file="version.txt"
            )
    assert "Invalid version format" in str(exc_info.value)

@patch.dict(os.environ, {'GITHUB_OUTPUT': 'github_output.txt'})
@patch("get_version.get_tags")
def test_empty_version_file(mock_get_tags):
    """Test handling of empty version file"""
    # Setup
    mock_get_tags.return_value = ["test-1.0.0"]  # Provide some tags to avoid no tags error
    
    with pytest.raises(ValueError) as exc_info:
        with patch("builtins.open", mock_open(read_data="")):
            get_latest_tag_with_module(
                module="test",
                version_file="version.txt"
            )
    assert "Empty version file" in str(exc_info.value)

@patch.dict(os.environ, {'GITHUB_OUTPUT': 'github_output.txt'})
@patch("get_version.get_tags")
def test_no_tags_found(mock_get_tags):
    """Test handling of no tags found"""
    # Setup
    mock_get_tags.return_value = []
    
    with pytest.raises(ValueError) as exc_info:
        with patch("builtins.open", mock_open(read_data="1.0.0")):
            get_latest_tag_with_module(
                module="test",
                version_file="version.txt"
            )
    assert "No tags found" in str(exc_info.value) 