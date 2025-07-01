import pytest
import os
from unittest.mock import patch, mock_open
from get_version import process, get_latest_tag_with_module

@patch("builtins.open", new_callable=mock_open, read_data="1.0.0")
@patch("get_version.get_tags")
@patch("get_version.set_output")
def test_empty_tag_list(mock_set_output, mock_get_tags, mock_file):
    # Mock empty tags list
    mock_get_tags.return_value = []
    mock_set_output.return_value = None

    # Should create a new tag based on version file content instead of raising error
    result = get_latest_tag_with_module(
        module="node",
        version_file="version.txt"
    )
    assert result == "node-1.0.0"


@pytest.fixture
def mock_file(mocker):
    mock = mock_open()
    mocker.patch("builtins.open", mock)
    return mock


@patch.dict(os.environ, {'GITHUB_OUTPUT': 'github_output.txt'})
@patch("get_version.get_tags")
@patch("get_version.set_output")
def test_special_characters_in_module(mock_set_output, mock_get_tags):
    """Test that module names with special characters are rejected"""
    mock_get_tags.return_value = ["test@module-1.0.0"]
    mock_set_output.return_value = None
    
    invalid_modules = [
        "test@module",  # @ symbol
        "test/module",  # forward slash
        "test\\module", # backslash
        "test!module",  # exclamation mark
        "test#module",  # hash
        "test$module",  # dollar sign
        "test%module",  # percent
        "test&module",  # ampersand
        "test*module",  # asterisk
    ]
    
    for invalid_module in invalid_modules:
        with pytest.raises(ValueError) as exc_info:
            with patch("builtins.open", mock_open(read_data="1.0.0")):
                get_latest_tag_with_module(
                    module=invalid_module,
                    version_file="version.txt"
                )
        assert "Invalid module name" in str(exc_info.value)
        assert "Only alphanumeric characters" in str(exc_info.value)

@patch("builtins.open", new_callable=mock_open, read_data="999999.999999.999999")
@patch("get_version.get_tags")
@patch("get_version.set_output")
def test_large_version_numbers(mock_set_output, mock_get_tags, mock_file):
    mock_get_tags.return_value = ["node-999999.999999.999999"]
    mock_set_output.return_value = None
    
    result = get_latest_tag_with_module(
        module="node",
        version_file="version.txt"
    )
    # The patch version should increment
    assert result == "node-999999.999999.1000000"

# Test mixed version formats
@patch("get_version.get_tags")
@patch("get_version.set_output")
def test_mixed_version_formats(mock_set_output, mock_get_tags):
    mock_get_tags.return_value = [
        "node-1.0", "node-1.0.0", "node-1"
    ]
    mock_set_output.return_value = None
    version_file = os.path.join(os.path.dirname(__file__), "test_resources/version_mixed.txt")
    
    with pytest.raises(ValueError):
        get_latest_tag_with_module(
            module="node",
            version_file=version_file
        ) 
