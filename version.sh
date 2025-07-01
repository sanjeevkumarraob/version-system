#!/bin/bash
set -eu

# Updated to use the new improved main.py instead of get_version.py
command_args=("main.py")

if [ -z "${VERSION_FILE:-}" ]; then
    echo "Version file is not present in environment variable"
    exit 1 
elif [ -z "${GIT_REPO_PATH:-}" ]; then
    echo "GIT_REPO_PATH is not present in environment variable"
    exit 1 
elif [ ! -z "${PREFIX:-}" ]; then
    echo "Prefix present in environment variable"
    VERSION_FILE="${GIT_REPO_PATH}/${VERSION_FILE}"
    command_args+=("-p" "${PREFIX}" "-f" "${VERSION_FILE}" "-r" "${GIT_REPO_PATH}")
elif [ ! -z "${SUFFIX:-}" ]; then
    echo "Suffix present in environment variable"
    VERSION_FILE="${GIT_REPO_PATH}/${VERSION_FILE}"
    command_args+=("-s" "${SUFFIX}" "-f" "${VERSION_FILE}" "-r" "${GIT_REPO_PATH}")
elif [ ! -z "${MODULE:-}" ]; then
    echo "Module present in environment variable"
    VERSION_FILE="${GIT_REPO_PATH}/${VERSION_FILE}"
    command_args+=("-m" "${MODULE}" "-f" "${VERSION_FILE}" "-r" "${GIT_REPO_PATH}")
else
    echo "Getting a simple semver"
    VERSION_FILE="${GIT_REPO_PATH}/${VERSION_FILE}"
    command_args+=("-f" "${VERSION_FILE}" "-r" "${GIT_REPO_PATH}")
fi

# FIXED: Only add -i flag when IS_SNAPSHOT is explicitly "true"
if [ ! -z "${IS_SNAPSHOT:-}" ] && [ "${IS_SNAPSHOT}" = "true" ]; then
    echo "Getting a snapshot version"
    command_args+=("-i")
fi

if [ ! -z "${BRANCH:-}" ]; then
  echo "Branch present in environment variable"
  command_args+=("-b" "${BRANCH}")
fi

echo "Command: ${command_args[@]}"

# Add git repo to safe directory list
git config --global --add safe.directory "${GIT_REPO_PATH}"

# Install dependencies if requirements.txt exists
if [ -f "$GITHUB_ACTION_PATH/requirements.txt" ]; then
    echo "Installing Python dependencies..."
    pip3 install -r $GITHUB_ACTION_PATH/requirements.txt
fi

# Run the improved Python script with the variables
python3 "$GITHUB_ACTION_PATH/${command_args[@]}"
