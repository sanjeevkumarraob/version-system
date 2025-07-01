import get_version as get_version
import os
import pytest
import sys
from unittest.mock import patch
from utils import utils

logger = utils.get_logger()

sys.dont_write_bytecode = True

GIT_TAG_RETURN_VALUE = ["1.6-dev","1.7-dev","3.0-dev","3.1-dev","3.1-dev-SNAPSHOT", "3.2-dev"]
SUFFIX_VERSION_FILE_PATH = "./tests/unit/test_suffix/test_resources/version.txt"


def read_version_file(file_name):
    pwd = os.path.dirname(__file__)
    test_resources_path = f"{pwd}/test_resources"
    result = open(f"{test_resources_path}/{file_name}", 'r').read()
    return result


def test_get_latest_tag_golden_path():
    version_to_check = read_version_file("version.txt")
    print(version_to_check)
    suffixRegexHyphen = get_version.suffixRegexHyphen;
    print(suffixRegexHyphen)
    try:
        match = suffixRegexHyphen.match(version_to_check)
        print(match)
        assert True
    except Exception:
        assert False


def test_sort_tag_suffix():
    version_to_check = read_version_file("version.txt")
    suffixRegexHyphen = get_version.suffixRegexHyphen;
    tags = ["1.0.0-dev", "1.0.1-dev", "1.0.10-dev", "1.0.2-dev", "1.0.3-dev", "1.0.4-dev", "1.0.5-dev", "1.0.6-dev", "1.0.7-dev", "1.0.8-dev", "1.0.9-dev"]
    suffix = "dev"
    tags_without_suffix = [tag.replace(f"-{suffix}", "") for tag in tags]
    sorted_tags = sorted(tags_without_suffix, key=lambda x: [int(num) if num.isdigit() else num for num in x.split('.')])
    sortedtags_with_suffix = [tag + f"-{suffix}" for tag in sorted_tags]
    current_tag = sortedtags_with_suffix[-1]
    tag = current_tag.split("-")[0]
    
    try:
        match = suffixRegexHyphen.match(version_to_check)
        print(match)
        assert True
    except Exception:
        assert False


def test_fail_suffix_snapshot():
    with pytest.raises(Exception) as excinfo:
        get_version.process(
            suffix="snapshot",
            version_file="version.txt"
        )
        assert excinfo is not None
        assert "Key word, SNAPSHOT, cannot be used for PREFIX or SUFFIX" == str(excinfo.value)


def test_append_snapshot_version_no_current_tag_return_next_tag():
    version_tag = get_version.append_snapshot_version(next_tag="1.0.0-dev")
    assert "1.0.0-dev" == version_tag


def test_append_snapshot_version_return_version():
    version_tag = get_version.append_snapshot_version(current_tag="1.0.0-dev", next_tag="1.1.0-dev")
    assert "1.1.0-dev" == version_tag


def test_append_snapshot_version_return_version_snapshot():
    version_tag = get_version.append_snapshot_version(current_tag="1.0.0-dev", next_tag="1.1.0-dev", is_snapshot=True)
    assert "1.1.0-dev-SNAPSHOT" == version_tag


def test_append_snapshot_version_return_version_branch_snapshot():
    version_tag = get_version.append_snapshot_version(current_tag="1.0.0-dev", next_tag="1.1.0-dev",
                                                      is_snapshot=True, branch="feature/PROJ-1234-test-branch")
    assert "1.1.0-dev-feature-PROJ-1234-te-SNAPSHOT" == version_tag


def test_append_snapshot_version_return_initial_version_branch_snapshot():
    version_tag = get_version.append_snapshot_version(next_tag="1.1.0-dev",
                                                      is_snapshot=True, branch="feature/PROJ-1234-test-branch")
    assert "0.0.1-feature-PROJ-1234-te-SNAPSHOT" == version_tag


def test_get_latest_tag_with_suffix_keyword_throw_exception():
    with pytest.raises(Exception) as excinfo:
        get_version.get_latest_tag_with_suffix(
            suffix="abc/def",
            version_file="version.txt"
        )
        assert excinfo is not None
        assert "Key word, /, cannot be used for PREFIX or SUFFIX" == str(excinfo.value)


@patch("get_version.set_output")
@patch("get_version.get_tags")
def test_get_latest_tag_with_suffix_no_snapshot(mock_get_tags, github_set_output):
    mock_get_tags.return_value = GIT_TAG_RETURN_VALUE
    github_set_output.return_value = None
    suffix_version = get_version.get_latest_tag_with_suffix(
        suffix="dev",
        version_file=SUFFIX_VERSION_FILE_PATH
    )
    assert "3.3-dev" == suffix_version


@patch("get_version.set_output")
@patch("get_version.get_tags")
def test_get_latest_tag_with_suffix_with_higher_version_no_snapshot(
    mock_get_tags, github_set_output
):
    mock_get_tags.return_value = GIT_TAG_RETURN_VALUE + [
        "3.3-dev",
        "3.10-dev",
        "3.30-dev",
        "3.31-dev",
        "3.40-dev",
    ]
    github_set_output.return_value = None
    suffix_version = get_version.get_latest_tag_with_suffix(
        suffix="dev",
        version_file=SUFFIX_VERSION_FILE_PATH
    )
    assert "3.41-dev" == suffix_version


@patch("get_version.set_output")
@patch("get_version.get_tags")
def test_get_latest_tag_with_suffix_snapshot(mock_get_tags, github_set_output):
    mock_get_tags.return_value = GIT_TAG_RETURN_VALUE
    github_set_output.return_value = None
    suffix_version = get_version.get_latest_tag_with_suffix(
        suffix="dev",
        version_file=SUFFIX_VERSION_FILE_PATH,
        is_snapshot=True
    )
    assert "3.3-dev-SNAPSHOT" == suffix_version


@patch("get_version.set_output")
@patch("get_version.get_tags")
def test_get_latest_tag_with_suffix_branch_snapshot(mock_get_tags, github_set_output):
    mock_get_tags.return_value = GIT_TAG_RETURN_VALUE + [
        "3.2-dev-feature-PROJ-1334-te-SNAPSHOT"
    ]
    github_set_output.return_value = None
    version = get_version.get_latest_tag_with_suffix(
        suffix="dev",
        version_file=SUFFIX_VERSION_FILE_PATH,
        branch="feature/PROJ-1234-test-branch",
        is_snapshot=True
    )
    assert "3.3-dev-feature-PROJ-1234-te-SNAPSHOT" == version


@patch("get_version.set_output")
@patch("get_version.get_tags")
def test_get_latest_tag_with_suffix_branch_snapshot_existing(
    mock_get_tags, github_set_output
):
    mock_get_tags.return_value = GIT_TAG_RETURN_VALUE + [
        "3.3-dev-feature-PROJ-1234-te-SNAPSHOT"
    ]
    github_set_output.return_value = None
    version = get_version.get_latest_tag_with_suffix(
        suffix="dev",
        version_file=SUFFIX_VERSION_FILE_PATH,
        branch="feature/PROJ-1234-test-branch",
        is_snapshot=True
    )
    assert "3.3-dev-feature-PROJ-1234-te-SNAPSHOT" == version


@patch("get_version.set_output")
@patch("get_version.get_tags")
def test_get_latest_tag_with_suffix_initial_snapshot(mock_get_tags, github_set_output):
    mock_get_tags.return_value = ""
    github_set_output.return_value = None
    version = get_version.get_latest_tag_with_suffix(
        suffix="dev",
        version_file=SUFFIX_VERSION_FILE_PATH,
        is_snapshot=True
    )
    assert "0.0.1-dev-SNAPSHOT" == version


@patch("get_version.set_output")
@patch("get_version.get_tags")
def test_get_latest_tag_with_suffix_initial(mock_get_tags, github_set_output):
    mock_get_tags.return_value = ""
    github_set_output.return_value = None
    version = get_version.get_latest_tag_with_suffix(
        suffix="dev",
        version_file=SUFFIX_VERSION_FILE_PATH
    )
    assert "3.0-dev" == version


# def test_get_latest_tag_fail_prefix():
#     version_to_check = read_version_file("wrong_version_prefix.txt")
#     print(version_to_check)
#     print(get_version.get_semver_regex())
#     match = get_version.get_semver_regex().match(version_to_check)
#     logger.info(f"""match regex is {match}""")

#     """
#     The semver regex match should return 'None' for all tags
#     which doesn't follow digit.digit.digit pattern

#     This test case will fail if the regex returns any object other than 'None'
#     """

#     assert match is None


# def test_get_latest_tag_fail_semver():
#     version_to_check = read_version_file("wrong_version_semver.txt")
#     print(version_to_check)
#     print(get_version.get_semver_regex())
#     match = get_version.get_semver_regex().match(version_to_check)
#     logger.info(f"""match regex is {match}""")

#     """
#     The semver regex match should return 'None' for all tags
#     which doesn't follow digit.digit.digit pattern

#     This test case will fail if the regex returns any object other than 'None'
#     """

#     assert match is None
