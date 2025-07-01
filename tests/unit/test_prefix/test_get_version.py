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

    # Assert that the result is the expected tag
    # Since there are no tags found and version.txt contains "1.0.0",
    # the result should be "1.0.0" (base version from file)
    assert result == "1.0.0"
