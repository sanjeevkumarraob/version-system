#!/bin/bash
set -eu

# Updated to use the new improved main.py instead of get_version.py

if [ -z "${VERSION_FILE:-}" ]; then
    echo "Version file is not present in environment variable"
    exit 1 
elif [ -z "${GIT_REPO_PATH:-}" ]; then
    echo "GIT_REPO_PATH is not present in environment variable"
    exit 1 
fi

# Add git repo to safe directory list
git config --global --add safe.directory "${GIT_REPO_PATH}"

# Install dependencies if requirements.txt exists
if [ -f "$GITHUB_ACTION_PATH/requirements.txt" ]; then
    echo "Installing Python dependencies..."
    pip3 install -r $GITHUB_ACTION_PATH/requirements.txt
fi

# Build command arguments
VERSION_FILE="${GIT_REPO_PATH}/${VERSION_FILE}"

# Build the command with proper argument handling
if [ ! -z "${PREFIX:-}" ]; then
    echo "Prefix present in environment variable"
    cmd="python3 \"$GITHUB_ACTION_PATH/main.py\" -p \"${PREFIX}\" -f \"${VERSION_FILE}\" -r \"${GIT_REPO_PATH}\""
elif [ ! -z "${SUFFIX:-}" ]; then
    echo "Suffix present in environment variable"
    cmd="python3 \"$GITHUB_ACTION_PATH/main.py\" -s \"${SUFFIX}\" -f \"${VERSION_FILE}\" -r \"${GIT_REPO_PATH}\""
elif [ ! -z "${MODULE:-}" ]; then
    echo "Module present in environment variable"
    cmd="python3 \"$GITHUB_ACTION_PATH/main.py\" -m \"${MODULE}\" -f \"${VERSION_FILE}\" -r \"${GIT_REPO_PATH}\""
else
    echo "Getting a simple semver"
    cmd="python3 \"$GITHUB_ACTION_PATH/main.py\" -f \"${VERSION_FILE}\" -r \"${GIT_REPO_PATH}\""
fi

# Add optional flags
if [ ! -z "${IS_SNAPSHOT:-}" ] && [ "${IS_SNAPSHOT}" = "true" ]; then
    echo "Getting a snapshot version"
    cmd="${cmd} -i"
fi

if [ ! -z "${BRANCH:-}" ]; then
    echo "Branch present in environment variable"
    cmd="${cmd} -b \"${BRANCH}\""
fi

echo "Executing: ${cmd}"

# Execute the command
eval "${cmd}"
