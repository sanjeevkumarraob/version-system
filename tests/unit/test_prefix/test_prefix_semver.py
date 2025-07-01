import os
import get_version as get_version
import sys
from unittest.mock import patch
from utils import utils

sys.dont_write_bytecode = True

logger = utils.get_logger()


def read_version_file(file_name):
    pwd = os.path.dirname(__file__)
    test_resources_path = f"{pwd}/test_resources"
    result = open(f"{test_resources_path}/{file_name}", 'r').read()
    return result
    

def test_get_latest_tag_golden_path():
    version_to_check = read_version_file("version.txt")
    print(version_to_check)
    prefixRegexHyphen = get_version.prefixRegexHyphen;
    print(prefixRegexHyphen)
    match = get_version.get_semver_regex().match(version_to_check)
    assert match is None


# def test_get_latest_tag_fail_prefix():
#     version_to_check = read_version_file("test_semver","wrong_version_prefix.txt")
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
    

# def test_get_latest_tag_fail_suffix():
#     version_to_check = read_version_file("test_semver","wrong_version_suffix.txt")
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
    
    
