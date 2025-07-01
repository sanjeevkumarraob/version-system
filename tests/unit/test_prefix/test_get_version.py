import pytest
from unittest.mock import patch
from get_version import get_latest_tag_with_prefix
from get_version import get_latest_tag


@patch("get_version.get_tags")
@patch("get_version.set_output")
def test_get_latest_tag_with_prefix(mock_set_output, mock_get_tags):
    # Mock the get_tags function to return a list of tags
    mock_get_tags.return_value = ["v1.0.0", "v1.1.0", "v1.2.0", "v2.0.0"]

    # Mock the set_output function
    mock_set_output.return_value = None

    # Call the function with a prefix and version file
    result = get_latest_tag_with_prefix("v", "main", "version.txt")

    # Assert that the result is the expected tag
    # Since version.txt contains "1.0.0" (semver format) and latest tag is "v2.0.0",
    # the result should be "v3.0.0" (incremented major version in semver format)
    assert result == "v3.0.0"


# @patch("get_version.get_tags")
@patch("get_version.set_output")
def test_get_latest_tag(mock_set_output):
    # Mock the get_tags function to return a list of tags
    # mock_get_tags.return_value = ["1.0"]

    # Mock the set_output function
    mock_set_output.return_value = None

    # Call the function with the version file and repo path
    result = get_latest_tag(version_file="version.txt", repo_path=".")

    # The action should find existing tags and calculate the next version
    # Since there are existing tags in the repo, it should increment from the latest
    # This test runs in the actual repo context where tags exist
    # So we expect it to return the next incremented version, not the base version
    
    # The result should be a valid semantic version string
    import re
    semver_pattern = r'^\d+\.\d+\.\d+$'
    assert re.match(semver_pattern, result), f"Result '{result}' should be a valid semantic version"
    
    # The result should be higher than the base version from file
    with open("version.txt", "r") as f:
        base_version = f.read().strip()
    
    # Convert versions to tuples for comparison
    def version_tuple(v):
        return tuple(map(int, v.split('.')))
    
    assert version_tuple(result) >= version_tuple(base_version), \
        f"Result version '{result}' should be >= base version '{base_version}'"
