"""
Custom exception classes for version system operations
"""

class VersionSystemError(Exception):
    """Base exception for all version system errors"""
    
    def __init__(self, message: str, details: dict = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}
    
    def __str__(self):
        if self.details:
            return f"{self.message} | Details: {self.details}"
        return self.message


class InvalidVersionError(VersionSystemError):
    """Raised when version format is invalid"""
    
    def __init__(self, version: str, expected_pattern: str = None):
        message = f"Invalid version format: '{version}'"
        if expected_pattern:
            message += f" (expected pattern: {expected_pattern})"
        
        # Add helpful suggestions
        suggestions = []
        if version and not any(c.isdigit() for c in version):
            suggestions.append("Version must contain numeric components")
        if version and '..' in version:
            suggestions.append("Remove consecutive dots")
        if version and (version.startswith('-') or version.endswith('-')):
            suggestions.append("Remove leading/trailing hyphens")
        
        if suggestions:
            message += f". Suggestions: {'; '.join(suggestions)}"
        
        details = {
            'invalid_version': version,
            'expected_pattern': expected_pattern,
            'suggestions': suggestions
        }
        super().__init__(message, details)


class TagNotFoundError(VersionSystemError):
    """Raised when no suitable tags are found"""
    
    def __init__(self, pattern: str = None, module: str = None):
        if pattern:
            message = f"No tags found matching pattern: '{pattern}'"
            details = {'pattern': pattern}
        elif module:
            message = f"No tags found for module: '{module}'"
            details = {'module': module}
        else:
            message = "No suitable tags found in repository"
            details = {}
        
        super().__init__(message, details)


class GitOperationError(VersionSystemError):
    """Raised when git operations fail"""
    
    def __init__(self, operation: str, stderr: str = None, exit_code: int = None):
        message = f"Git operation failed: {operation}"
        details = {
            'operation': operation,
            'stderr': stderr,
            'exit_code': exit_code
        }
        super().__init__(message, details)


class ValidationError(VersionSystemError):
    """Raised when input validation fails"""
    
    def __init__(self, field: str, value: str, reason: str):
        message = f"Validation failed for {field}: {reason}"
        
        # Add context-specific help
        help_text = ""
        if field == "module_name":
            help_text = " (Module names must start/end with alphanumeric characters and can contain hyphens, dots, underscores)"
        elif field == "file_path":
            help_text = " (Ensure the file exists and path is valid)"
        elif field == "increment_type":
            help_text = " (Valid types: major, minor, patch)"
        
        message += help_text
        
        details = {
            'field': field,
            'value': value,
            'reason': reason,
            'help': help_text.strip()
        }
        super().__init__(message, details)


class ConfigurationError(VersionSystemError):
    """Raised when configuration is invalid or missing"""
    
    def __init__(self, config_key: str, reason: str):
        message = f"Configuration error for '{config_key}': {reason}"
        details = {
            'config_key': config_key,
            'reason': reason
        }
        super().__init__(message, details)
