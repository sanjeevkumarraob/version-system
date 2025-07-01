# Get New tag for a branch
import argparse
import os
import re
import sys
import subprocess
from utils import utils

sys.dont_write_bytecode = True

logger = utils.get_logger()
repo=""
TAG_SEPARATOR = "-"
SNAPSHOT = "SNAPSHOT"
semverRegex = re.compile(r'^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$')
moduleRegex = re.compile(r'(.+)-(\d+\.\d+\.\d+)$')  # Will match any module with semver
moduleRegexMajorMinor = re.compile(r'(.+)-(\d+\.\d+)$')  # Will match any module with major.minor
moduleTagRegexMajorMinor = re.compile(
    r"^(\d+\.\d+\.\d+\.\d+)-(\d+\.\d+)$"
)  # "3.7.1.2-2.0"

majorVersionRegex = re.compile(r'^(0|[1-9]\d*)$')
minorVersionRegex = re.compile(r'^(0|[1-9]\d*)\.(0|[1-9]\d*)$')
prefixRegexHyphen = re.compile(r'^([a-zA-z]+)\-([0-9]\d*\.[0-9]\d*\.[0-9]\d*)$') #snapshot-1.2.3
prefixRegexHyphenMajorMinor = re.compile(r'^([a-zA-z]+)\-([0-9]\d*\.[0-9]\d*)$') #snapshot-1.2
prefixRegexDot = re.compile(r'^([a-zA-z]+)\.([0-9]\d*\.[0-9]\d*\.[0-9]\d*)$') #R.11.23.0
prefixRegexPlain = re.compile(r'^([a-zA-z]+)([0-9]\d*\.[0-9]\d*\.[0-9]\d*)$') #v1.1.0
prefixRegexMajor = re.compile(r'^([a-zA-z]+)([0-9]\d*)$')  # v1, v2 etc.,
prefixRegexMajorMinor = re.compile(r'^([a-zA-z]+)([0-9]\d*\.[0-9]\d*)$')  # v1.1, v2.2 etc.,
suffixRegexHyphen = re.compile(r'^([0-9]\d*\.[0-9]\d*\.[0-9]\d*)\-([a-zA-z]+)$') #1.2.3-snapshot
suffixRegexHyphenMajorMinor = re.compile(r'^([0-9]\d*\.[0-9]\d*)\-([a-zA-z]+)$') #1.2-snapshot

MODULE_NAME_PATTERN = r'^[a-zA-Z0-9][a-zA-Z0-9\-\._]*[a-zA-Z0-9]$'

def validate_module_name(module):
    """
    Validates that the module name contains only allowed characters and follows the pattern.
    Allowed characters are:
    - Alphanumeric (a-z, A-Z, 0-9)
    - Hyphen (-)
    - Dot (.)
    - Underscore (_)
    Must start and end with alphanumeric character.
    """
    if not module:
        raise ValueError("Module name cannot be empty")
        
    if not re.match(MODULE_NAME_PATTERN, module):
        raise ValueError(
            "Invalid module name. Only alphanumeric characters, hyphens, dots, and underscores are allowed. "
            "Must start and end with alphanumeric character."
        )

def get_semver_regex():
    return semverRegex


def get_tags(
    pattern=None, repo_path=".", version_file=None, is_prefix=True, module=None
):
    """
    Get the tags from the git repo matching the specified pattern, version, and module.
    :param pattern: the pattern to search for the tags (prefix or suffix)
    :param repo_path: the path to the git repo
    :param version_file: path to the version file (version.txt or floating_version.txt)
    :param is_prefix: boolean indicating if the pattern is a prefix (True) or suffix (False)
    :param module: module name to be used as a prefix
    :return: a list of tags
    """
    print("Getting tags from the git repo")
    print("Pattern is", pattern)
    print("Is prefix:", is_prefix)
    print("Module:", module)

    if not version_file:
        raise ValueError("Version file must be provided")

    # Get all tags
    output = subprocess.run(
        ["git", "tag", "-l", "--sort", "refname"],
        cwd=repo_path,
        stdout=subprocess.PIPE,
        text=True,
    )
    all_tags = output.stdout.strip().split("\n")

    # Read the version from the file
    with open(version_file, "r") as f:
        version = f.read().strip()

    # Determine the version pattern based on the content of version file
    if majorVersionRegex.match(version):
        version_pattern = r"(\d+)"
    elif minorVersionRegex.match(version):
        version_pattern = r"(\d+\.\d+)"
    elif semverRegex.match(version):
        version_pattern = r"(\d+\.\d+\.\d+)"
    else:
        version_pattern = r"(\d+(\.\d+)*)"

    def filter_tag(tag):
        if pattern:
            if is_prefix:
                return tag.startswith(pattern) and re.search(
                    rf"{re.escape(pattern)}{version_pattern}$", tag
                )
            else:
                return tag.endswith(f"-{pattern}") and re.search(
                    rf"{version_pattern}-{re.escape(pattern)}$", tag
                )
        elif module:
            return tag.startswith(f"{module}-") and re.search(
                rf"{module}-{version_pattern}$", tag
            )
        else:
            return re.match(f"{version_pattern}$", tag)

    filtered_tags = list(filter(filter_tag, all_tags))
    return sorted(filtered_tags, key=lambda x: [int(n) for n in re.findall(r"\d+", x)])


def increase_version(version, version_file):
    # Read the base version from the version file
    f = open(version_file, "r")
    base_version = f.read().strip()
    version = str(version)
    next_tag = ""
    if re.match(semverRegex, base_version):
        print("Version pattern follows a semver.. increasing the patch version")
        version = version.split('.')
        major_version = version[0]
        minor_version = version[1]
       
        base_major_version = base_version.split('.')[0]
        base_minor_version = base_version.split('.')[1]
        base_patch_version = base_version.split('.')[2]

        if (int(base_major_version) > int(major_version)):
            major_version = str(int(base_major_version))
            minor_version = base_minor_version
            patch_version = base_patch_version
        elif (int(base_major_version) == int(major_version)):
            try:
                patch_version = str(int(version[2])+1)
            except IndexError:
                patch_version = base_patch_version
        else:
            # When base major version is less than current major version,
            # increment the current major version and reset minor/patch
            major_version = str(int(major_version) + 1)
            minor_version = "0"
            patch_version = "0"

        next_tag = '.'.join([major_version, minor_version, patch_version])

    elif re.match(minorVersionRegex, base_version):
        print("Version pattern follows a minor version.. increasing the minor version")
        major_version = version.split('.')[0]
        minor_version = version.split('.')[1]

        base_major_version = base_version.split('.')[0]
        base_minor_version = base_version.split('.')[1]

        if (int(base_major_version) > int(major_version)):
            major_version = str(int(base_major_version))
            minor_version = base_minor_version
        elif (int(base_major_version) == int(major_version)):
            minor_version = str(int(minor_version)+1)
        else:
            logger.error(
                "Base major version cannot be less than current major version")

        next_tag = '.'.join([major_version, minor_version])
                
    elif re.match(majorVersionRegex, base_version):
        print("Version pattern follows a major version.. increasing the major version")
        major_version = version.split('.')[0]

        base_major_version = base_version.split('.')[0]

        if (int(base_major_version) > int(major_version)):
            major_version = str(int(base_major_version))
        elif (int(base_major_version) == int(major_version)):
            major_version = str(int(major_version)+1)
        else:
            logger.error(
                "Base major version cannot be less than current major version")

        next_tag = major_version

    else:
        logger.error("Version file is not following the standard")

    return next_tag


def append_snapshot_version(
    next_tag: str,
    prefix: str = None,
    suffix: str = None,
    current_tag: str = None,
    is_snapshot: bool = False,
    branch: str = None
) -> str:
    """
    return the version (along with snapshot and branch based on the condition).

    :param next_tag: the next release tag
    :param prefix: the prefix to be appended to the version
    :param suffix: the suffix to be appended to the version
    :param current_tag: the current tag
    :param is_snapshot: to denote whether it is a snapshot version. True or False
    :param branch: the branch name to be appended to the snapshot version
    :return: snapshot tag with branch name based on the condition
    """

    if is_snapshot:
        if current_tag:
            version = next_tag
        else:
            version = "0.0.1"

        version = append_prefix_suffix_tag(version=version, prefix=prefix, suffix=suffix)
        if branch:
            branch = branch.replace("/", "-")[:20]
            version = TAG_SEPARATOR.join([version, branch])
        version = TAG_SEPARATOR.join([version, SNAPSHOT])
    else:
        version = append_prefix_suffix_tag(version=next_tag, prefix=prefix, suffix=suffix)

    return version


def append_prefix_suffix_tag(
    version: str,
    prefix: str = None,
    suffix: str = None
) -> str:
    """
    Append the prefix or suffix to the version.
    :param version: version to be tagged
    :param prefix: prefix to be appended to version
    :param suffix: suffix to be appended to version
    :return:
    """
    if prefix:
        version = TAG_SEPARATOR.join([prefix, version])
    elif suffix:
        version = TAG_SEPARATOR.join([version, suffix])
    else:
        version = version
    return version


def get_latest_tag_with_prefix(prefix=None, branch=None, version_file=None, repo_path=None):
    tags = get_tags(pattern=prefix, is_prefix=True, repo_path=repo_path, version_file=version_file)
    print("Tags with Prefix", tags)
    # tags = repo.git.tag("--list", f"{prefix}*", "--sort", "refname")
    tag = ""
    if not tags:
        # No tags present. Read from the version file and create a base tag
        print("No Tags present... Creating a new tag based on the version file...")
        f = open(version_file, "r")
        latest_tag = f.read().strip()

    if len(tags) > 0:
       
        current_tag = tags[-1]
        print("current tag is ", current_tag)
        set_output("current_tag", current_tag)
        # strip off the prefix and just send the semver to increase the version
        if re.match(prefixRegexHyphen, current_tag):
            tagGroup = prefixRegexHyphen.search(current_tag)
            tag = tagGroup.group(2)
        elif re.match(prefixRegexHyphenMajorMinor, current_tag):
            tagGroup = prefixRegexHyphenMajorMinor.search(current_tag)
            tag = tagGroup.group(2)
        elif re.match(prefixRegexDot, current_tag):
            tagGroup = prefixRegexDot.search(current_tag)
            tag = tagGroup.group(2)
        elif re.match(prefixRegexPlain, current_tag):
            tagGroup = prefixRegexPlain.search(current_tag)
            tag = tagGroup.group(2)
        elif re.match(prefixRegexMajor, current_tag):
            tagGroup = prefixRegexMajor.search(current_tag)
            tag = tagGroup.group(2)
        elif re.match(prefixRegexMajorMinor, current_tag):
            tagGroup = prefixRegexMajorMinor.search(current_tag)
            tag = tagGroup.group(2)
        else:
            logger.error("Tag doesn't follow available combinations.. Please check the documentation")

        latest_tag = increase_version(tag, version_file)

    next_tag = "".join([prefix, latest_tag])
    print("latest tag is ", next_tag)
    set_output("next_tag", next_tag)
    return next_tag


def get_latest_tag_with_module(module=None, branch=None, version_file=None, repo_path=None):
    """Get the latest tag for a module"""
    # Validate module name first
    validate_module_name(module)
    
    # Validate version file
    try:
        with open(version_file, 'r') as f:
            version_content = f.read().strip()
            if not version_content:
                raise ValueError("Empty version file")
            if not (semverRegex.match(version_content) or 
                   majorVersionRegex.match(version_content) or 
                   minorVersionRegex.match(version_content)):
                raise ValueError("Invalid version format in version file")
    except FileNotFoundError:
        raise ValueError(f"Version file not found: {version_file}")
    
    # Get tags after validation
    tags = get_tags(module=module, repo_path=repo_path, version_file=version_file)
    
    print("Tags with Module", tags)
    
    if not tags:
        # No tags present. Read from the version file and create a base tag
        print("No Tags present... Creating a new tag based on the version file...")
        f = open(version_file, "r")
        latest_tag = f.read().strip()
    
    if len(tags) > 0:
        current_tag = tags[-1]  # Get the latest tag
        print("current tag is ", current_tag)
        set_output("current_tag", current_tag)
        
        # Extract version part by removing the module prefix
        # This handles both simple modules ("node-1.0.0") and complex ones ("my-node-1.0.0")
        version_part = current_tag.replace(f"{module}-", "", 1)
        
        # Validate that we actually found and removed the module prefix
        if version_part == current_tag:
            raise ValueError(f"Could not find module '{module}' in tag: {current_tag}")
            
        # Verify the version part matches expected format
        if re.match(r'^\d+\.\d+\.\d+$', version_part):
            latest_tag = increase_version(version_part, version_file)
        elif re.match(r'^\d+\.\d+$', version_part):
            latest_tag = increase_version(version_part, version_file)
        else:
            raise ValueError(f"Invalid version format in tag: {current_tag}")
    
    next_tag = f"{module}-{latest_tag}"
    print("latest tag is ", next_tag)
    set_output("next_tag", next_tag)
    return next_tag


def get_latest_tag_with_suffix(
    suffix: str,
    version_file: str,
    branch: str = None,
    is_snapshot: bool = False,
    repo_path=None,
) -> str:

    if TAG_SEPARATOR in suffix:
        raise Exception(f"Key word, {TAG_SEPARATOR}, cannot be used for SUFFIX")

    tags = get_tags(pattern=suffix, is_prefix=False, repo_path=repo_path, version_file=version_file)
    tag = ""
    current_tag = None
    if not tags:
        # No tags present. Read from the version file and create a base tag
        print("No Tags present... Creating a new tag based on the version file...")
        f = open(version_file, "r")
        latest_tag = f.read().strip()

    if len(tags) > 0:
        # tags = tags.split("\n")
        suffix_tags = [tag for tag in tags if tag.endswith("-" + suffix)]
        remove_snapshot_tags = [tag for tag in suffix_tags if SNAPSHOT not in tag]
        tags_version_only = [tag.split("-")[0] for tag in remove_snapshot_tags]
        sorted_tags = sorted(tags_version_only, key=lambda x: [int(i) if i.isdigit() else i for i in x.split('.')])
        sortedtags_with_suffix = [tag + f"-{suffix}" for tag in sorted_tags]
        current_tag = sortedtags_with_suffix[-1]
        print("current tag is ", current_tag)
        set_output("current_tag", current_tag)
        # strip off the suffix and just send the semver to increase the version
        tag = current_tag.split("-")[0]
        latest_tag = increase_version(tag, version_file)

    next_tag = append_snapshot_version(current_tag=current_tag, next_tag=latest_tag, suffix=suffix,
                                       is_snapshot=is_snapshot, branch=branch)
    print("latest tag is ", next_tag)
    set_output("next_tag", next_tag)
    return next_tag


def get_latest_tag(version_file: str = None, repo_path=None):
    tags = get_tags(repo_path=repo_path, version_file=version_file)
    print("all tags", tags)
    if not tags:
        # No tags present. Read from the version file and create a base tag
        print("No Tags present... Creating a new tag based on the version file...")
        f = open(version_file, "r")
        latest_tag = f.read().strip()

    if len(tags) > 0:
        # tagsList = tags.split("\n")
        current_tag = tags[-1]
        set_output("current_tag", current_tag)
        latest_tag = increase_version(current_tag, version_file)

    next_tag = latest_tag
    print("latest tag is ", next_tag)
    set_output("next_tag", next_tag)
    return next_tag


# set next_tag in github output


def set_output(name, value):
    with open(os.environ['GITHUB_OUTPUT'], 'a') as gho:
        print(f'{name}={value}', file=gho)


def process(
    branch: str = None,
    prefix: str = None,
    suffix: str = None,
    version_file: str = None,
    module: str = None,
    is_snapshot: bool = False,
    repo_path: str = None
) -> str:
    """
    :param prefix: Prefix for the tag (eg., dev, snapshot, beta)
    :param branch: Branch to get the latest tag and apply a new tag
    :param suffix: Suffix for the tag (eg., rc)
    :param version_file: Version reference file to get the base tag.
    :param module: Specify the module to be tagged (eg., a folder inside a repo to be tagged differently)
    :param is_snapshot: if this is True, then create SNAPSHOT tag
    """
    logger.info(
        f"""
        Processing next tag...
        prefix={prefix}
        branch={branch}
        suffix={suffix}
        version_file={version_file}
        module={module}
        """
    )

    # Check if the prefix or suffix is SNAPSHOT and not None
    if suffix is not None and suffix.upper() == SNAPSHOT or prefix is not None and prefix.upper() == SNAPSHOT:
        raise Exception(f"Key word, {SNAPSHOT}, cannot be used for PREFIX or SUFFIX")

    if prefix != None:
        # Use the prefix to get the latest tag for the pattern
        # Use the prefix to create a new tag.
        next_tag = get_latest_tag_with_prefix(prefix=prefix,
         branch=branch, 
         version_file=version_file, 
         repo_path=repo_path)
    elif suffix != None:
        # Use the suffix to get the latest tag for the pattern
        # Use the suffix to create a new tag.
        next_tag = get_latest_tag_with_suffix(
            suffix=suffix,
            branch=branch,
            version_file=version_file,
            is_snapshot=is_snapshot,
            repo_path=repo_path
        )
    elif module != None:
        # Use module as a prefix to identify the version and increase the module version
        next_tag = get_latest_tag_with_module(
            module=module, 
            branch=branch, 
            version_file=version_file, 
            repo_path=repo_path
        )
    else:
        logger.info("Creating a plain semver tag...")
        next_tag = get_latest_tag(
            version_file=version_file,
            repo_path=repo_path
            )

    # print("Next Tag from process ", next_tag)
    return next_tag


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Get the next tag for the repo')
    parser.add_argument('-p', '--prefix', dest='prefix', metavar='snapshot',
                        help='Prefix for the tag eg., dev-1.0.0')
    parser.add_argument('-b', '--branch', dest='branch',
                        help='Provide the branch to look for the tags/tag a specific branch', required=False)
    parser.add_argument('-f', '--version-file', dest='version_file',
                        help='Provide the version file for base tag', required=True)
    parser.add_argument('-s', '--suffix', dest='suffix',
                        help='Suffix for the tag. eg., 1.0.0-rc')
    parser.add_argument('-m', '--module', dest='module',
                        help='Create a tag for a module in the repo.')
    parser.add_argument('-r', '--git-repo-path', dest='git_repo_path',
                        help='Git repo path.')
    parser.add_argument('-i', '--is-snapshot', dest='is_snapshot',
                        help='Create a SNAPSHOT tag', required=False)

    args = parser.parse_args()
    # repo = utils.get_repo(args.git_repo_path)
    current_branch = utils.get_repo_branch(args.git_repo_path)
    print("Current branch is ", current_branch)
    try:
        process(
            prefix=None if args.prefix == "" else args.prefix,
            branch=None if args.branch == "" else args.branch,
            version_file=None if args.version_file == "" else args.version_file,
            suffix=None if args.suffix == "" else args.suffix,
            module=None if args.module == "" else args.module,
            is_snapshot=False if args.is_snapshot == "" else args.is_snapshot,
            repo_path=None if args.git_repo_path == "" else args.git_repo_path
        )
    except Exception as exp:
        logger.exception(exp, stack_info=True, exc_info=True)
        sys.exit(1)
