"""
Utility functions
"""
import sys
sys.dont_write_bytecode = True
import logging
import os
import re
import subprocess
from logging import Logger
from urllib import parse

def get_logger() -> Logger:
    """
    Get logger

    :return: logger
    """
    return logger


def __create_logger() -> Logger:
    formatter = logging.Formatter(
        fmt="%(asctime)s - %(levelname)s - %(module)s - %(message)s"
    )
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)
    handler.setFormatter(formatter)
    version_logger = logging.getLogger("version_system")
    version_logger.setLevel(logging.INFO)
    version_logger.addHandler(handler)
    return version_logger


def raise_error(error_message: str):
    """
    Raise an exception with an error message

    :param error_message: exception message
    :return: return exception with a message
    """
    raise Exception(error_message)

logger = __create_logger()

# def get_repo(repo_path: str):
#     """
#     Get Repo object for the given path
#     """
#     repo = git.Repo(repo_path)
#     return repo


def get_repo_branch(repo_path: str) -> str:
    """
    Get the current branch name of the repository at the given path using subprocess.
    """
    result = subprocess.run(
        ["git", "-C", repo_path, "rev-parse", "--abbrev-ref", "HEAD"],
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        return result.stdout.strip()
    else:
        raise Exception(f"Failed to get repo branch: {result.stderr}")
