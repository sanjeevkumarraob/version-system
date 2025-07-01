import pytest
import os
from unittest.mock import patch
from get_version import process

def get_resource_path(filename):
    return os.path.join(os.path.dirname(__file__), "test_resources", filename)

@patch.dict(os.environ, {'GITHUB_OUTPUT': 'github_output.txt'})
@patch("get_version.get_tags")
@patch("get_version.set_output")
def test_process_with_prefix(mock_set_output, mock_get_tags):
    """Test process function with prefix"""
    # Setup
    mock_get_tags.return_value = ["v1.0.0"]
    mock_set_output.return_value = None
    version_file = get_resource_path("version_prefix.txt")
    
    # Test
    result = process(
        prefix="v",
        version_file=version_file
    )
    assert result.startswith("v") 