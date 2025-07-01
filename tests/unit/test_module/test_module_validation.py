import pytest
from get_version import validate_module_name

def test_valid_module_names():
    """Test various valid module name formats"""
    valid_names = [
        "my-cli",
        "my_cli",
        "my.cli",
        "myCli",
        "my-cli-v2",
        "my_cli_v2",
        "my.cli.v2",
        "api2",
        "a2b",
        "my-cli_v2.test",
        "my_cli-1.0.0",
        "my_module-2.1.0",
        "test_api.v2",
        "api_gateway-1.0",
    ]

    for name in valid_names:
        validate_module_name(name)  # Should not raise any exception


def test_invalid_module_names():
    """Test various invalid module name formats"""
    invalid_names = [
        "-my-cli",  # Starts with hyphen
        "_my_cli",  # Starts with underscore
        ".my.cli",  # Starts with dot
        "my-cli-",  # Ends with hyphen
        "my_cli_",  # Ends with underscore
        "my.cli.",  # Ends with dot
        "my cli",  # Contains space
        "my@cli",  # Contains special character
        "my/cli",  # Contains slash
        "@my_cli",  # Starts with special character
        "my_cli#",  # Ends with special character
    ]

    error_message = (
        "Invalid module name. Only alphanumeric characters, hyphens, dots, "
        "and underscores are allowed. Must start and end with alphanumeric character."
    )

    for name in invalid_names:
        with pytest.raises(ValueError) as exc_info:
            validate_module_name(name)
        assert str(exc_info.value) == error_message


def test_empty_module_name():
    """Test empty string module name"""
    with pytest.raises(ValueError) as exc_info:
        validate_module_name("")
    assert str(exc_info.value) == "Module name cannot be empty"


def test_module_name_with_version():
    """Test module names with version numbers"""
    valid_version_names = [
        "module_name-1.0.0",
        "api_gateway-2.1",
        "test_api-1.0.0-beta",
        "my_module-v1.0",
    ]
    
    for name in valid_version_names:
        validate_module_name(name)  # Should not raise any exception

def test_none_module_name():
    """Test that None module name raises ValueError"""
    with pytest.raises(ValueError) as exc_info:
        validate_module_name(None)
    assert str(exc_info.value) == "Module name cannot be empty"

def test_whitespace_module_name():
    """Test that whitespace-only module name is invalid"""
    error_message = (
        "Invalid module name. Only alphanumeric characters, hyphens, dots, "
        "and underscores are allowed. Must start and end with alphanumeric character."
    )
    
    with pytest.raises(ValueError) as exc_info:
        validate_module_name("   ")
    assert str(exc_info.value) == error_message 
