"""
Security utilities for safe file operations
"""

import os
from pathlib import Path
from typing import Optional
from ..exceptions import ValidationError


class SecurityValidator:
    """Handles security validation for file operations"""
    
    @staticmethod
    def validate_file_path(file_path: str, base_path: Optional[str] = None) -> str:
        """
        Validate and normalize a file path to prevent path traversal attacks
        
        Args:
            file_path: Path to validate
            base_path: Optional base path to restrict access to
            
        Returns:
            Normalized safe path
            
        Raises:
            ValidationError: If path is unsafe
        """
        if not file_path:
            raise ValidationError("file_path", file_path, "File path cannot be empty")
        
        # Normalize the path
        try:
            normalized_path = os.path.normpath(file_path)
            resolved_path = os.path.abspath(normalized_path)
        except Exception as e:
            raise ValidationError("file_path", file_path, f"Invalid path format: {str(e)}")
        
        # Check for path traversal attempts
        if '..' in normalized_path:
            raise ValidationError("file_path", file_path, "Path traversal not allowed")
        
        # Check for absolute paths outside base_path if specified
        if base_path:
            try:
                base_resolved = os.path.abspath(base_path)
                if not resolved_path.startswith(base_resolved):
                    raise ValidationError("file_path", file_path, f"Path outside allowed directory: {base_path}")
            except Exception as e:
                raise ValidationError("base_path", base_path, f"Invalid base path: {str(e)}")
        
        # Check if path exists and is a file
        if not os.path.exists(resolved_path):
            raise ValidationError("file_path", file_path, "File does not exist")
        
        if not os.path.isfile(resolved_path):
            raise ValidationError("file_path", file_path, "Path is not a file")
        
        return resolved_path
    
    @staticmethod
    def validate_directory_path(dir_path: str, base_path: Optional[str] = None) -> str:
        """
        Validate and normalize a directory path
        
        Args:
            dir_path: Directory path to validate
            base_path: Optional base path to restrict access to
            
        Returns:
            Normalized safe directory path
            
        Raises:
            ValidationError: If path is unsafe
        """
        if not dir_path:
            raise ValidationError("dir_path", dir_path, "Directory path cannot be empty")
        
        # Normalize the path
        try:
            normalized_path = os.path.normpath(dir_path)
            resolved_path = os.path.abspath(normalized_path)
        except Exception as e:
            raise ValidationError("dir_path", dir_path, f"Invalid path format: {str(e)}")
        
        # Check for path traversal attempts
        if '..' in normalized_path:
            raise ValidationError("dir_path", dir_path, "Path traversal not allowed")
        
        # Check for absolute paths outside base_path if specified
        if base_path:
            try:
                base_resolved = os.path.abspath(base_path)
                if not resolved_path.startswith(base_resolved):
                    raise ValidationError("dir_path", dir_path, f"Path outside allowed directory: {base_path}")
            except Exception as e:
                raise ValidationError("base_path", base_path, f"Invalid base path: {str(e)}")
        
        # Check if path exists and is a directory
        if not os.path.exists(resolved_path):
            raise ValidationError("dir_path", dir_path, "Directory does not exist")
        
        if not os.path.isdir(resolved_path):
            raise ValidationError("dir_path", dir_path, "Path is not a directory")
        
        return resolved_path
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """
        Sanitize a filename to remove dangerous characters
        
        Args:
            filename: Filename to sanitize
            
        Returns:
            Sanitized filename
        """
        if not filename:
            raise ValidationError("filename", filename, "Filename cannot be empty")
        
        # Remove dangerous characters
        dangerous_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|', '\0']
        sanitized = filename
        
        for char in dangerous_chars:
            sanitized = sanitized.replace(char, '_')
        
        # Remove leading/trailing dots and spaces
        sanitized = sanitized.strip('. ')
        
        if not sanitized:
            raise ValidationError("filename", filename, "Filename becomes empty after sanitization")
        
        return sanitized
