"""
Version parsing and validation utilities
"""

import re
from typing import Optional, List, Dict, Pattern
from ..models.version import VersionInfo, VersionType, VersionConfig
from ..exceptions import InvalidVersionError, ValidationError


class VersionParser:
    """Handles parsing and validation of version strings"""
    
    def __init__(self, config: Optional[VersionConfig] = None):
        self.config = config or VersionConfig()
        self._patterns = self._build_patterns()
    
    def _build_patterns(self) -> Dict[str, Pattern[str]]:
        """Build regex patterns for version parsing"""
        return {
            # Basic version patterns
            'semver': re.compile(r'^(\d+)\.(\d+)\.(\d+)$'),
            'major_minor': re.compile(r'^(\d+)\.(\d+)$'),
            'major': re.compile(r'^(\d+)$'),
            
            # Prefixed patterns
            'prefix_semver': re.compile(r'^([a-zA-Z][a-zA-Z0-9]*)-(\d+)\.(\d+)\.(\d+)$'),
            'prefix_major_minor': re.compile(r'^([a-zA-Z][a-zA-Z0-9]*)-(\d+)\.(\d+)$'),
            'prefix_major': re.compile(r'^([a-zA-Z][a-zA-Z0-9]*)-(\d+)$'),
            
            # Suffixed patterns
            'suffix_semver': re.compile(r'^(\d+)\.(\d+)\.(\d+)-([a-zA-Z][a-zA-Z0-9]*)$'),
            'suffix_major_minor': re.compile(r'^(\d+)\.(\d+)-([a-zA-Z][a-zA-Z0-9]*)$'),
            'suffix_major': re.compile(r'^(\d+)-([a-zA-Z][a-zA-Z0-9]*)$'),
            
            # Module patterns - consistent with validation rules
            'module_semver': re.compile(r'^([a-zA-Z0-9][a-zA-Z0-9\-\._]*[a-zA-Z0-9])-(\d+)\.(\d+)\.(\d+)$'),
            'module_major_minor': re.compile(r'^([a-zA-Z0-9][a-zA-Z0-9\-\._]*[a-zA-Z0-9])-(\d+)\.(\d+)$'),
            'module_major': re.compile(r'^([a-zA-Z0-9][a-zA-Z0-9\-\._]*[a-zA-Z0-9])-(\d+)$'),
            
            # Complex patterns (prefix + suffix)
            'prefix_suffix_semver': re.compile(r'^([a-zA-Z][a-zA-Z0-9]*)-(\d+)\.(\d+)\.(\d+)-([a-zA-Z][a-zA-Z0-9]*)$'),
        }
    
    def parse(self, version_string: str) -> VersionInfo:
        """
        Parse a version string into a VersionInfo object
        
        Args:
            version_string: The version string to parse
            
        Returns:
            VersionInfo object with parsed components
            
        Raises:
            InvalidVersionError: If the version string is invalid
        """
        if not version_string or not version_string.strip():
            raise InvalidVersionError(version_string, "Version string cannot be empty")
        
        version_string = version_string.strip()
        
        # Try to match against all patterns
        for pattern_name, pattern in self._patterns.items():
            match = pattern.match(version_string)
            if match:
                return self._parse_match(match, pattern_name, version_string)
        
        # If no pattern matches, raise an error
        raise InvalidVersionError(version_string, "No valid version pattern found")
    
    def _parse_match(self, match: re.Match, pattern_name: str, original: str) -> VersionInfo:
        """Parse a regex match into VersionInfo"""
        groups = match.groups()
        
        # Initialize version components
        major = minor = patch = None
        prefix = suffix = module = None
        
        if pattern_name == 'semver':
            major, minor, patch = map(int, groups)
        elif pattern_name == 'major_minor':
            major, minor = map(int, groups)
        elif pattern_name == 'major':
            major = int(groups[0])
        elif pattern_name == 'prefix_semver':
            prefix, major, minor, patch = groups[0], int(groups[1]), int(groups[2]), int(groups[3])
        elif pattern_name == 'prefix_major_minor':
            prefix, major, minor = groups[0], int(groups[1]), int(groups[2])
        elif pattern_name == 'prefix_major':
            prefix, major = groups[0], int(groups[1])
        elif pattern_name == 'suffix_semver':
            major, minor, patch, suffix = int(groups[0]), int(groups[1]), int(groups[2]), groups[3]
        elif pattern_name == 'suffix_major_minor':
            major, minor, suffix = int(groups[0]), int(groups[1]), groups[2]
        elif pattern_name == 'suffix_major':
            major, suffix = int(groups[0]), groups[1]
        elif pattern_name == 'module_semver':
            module, major, minor, patch = groups[0], int(groups[1]), int(groups[2]), int(groups[3])
            # Additional validation for module name consistency
            self.validate_module_name(module)
        elif pattern_name == 'module_major_minor':
            module, major, minor = groups[0], int(groups[1]), int(groups[2])
            # Additional validation for module name consistency
            self.validate_module_name(module)
        elif pattern_name == 'module_major':
            module, major = groups[0], int(groups[1])
            # Additional validation for module name consistency
            self.validate_module_name(module)
        elif pattern_name == 'prefix_suffix_semver':
            prefix, major, minor, patch, suffix = groups[0], int(groups[1]), int(groups[2]), int(groups[3]), groups[4]
        else:
            raise InvalidVersionError(original, f"Unknown pattern: {pattern_name}")
        
        return VersionInfo(
            major=major,
            minor=minor,
            patch=patch,
            prefix=prefix,
            suffix=suffix,
            module=module
        )
    
    def validate(self, version_string: str) -> bool:
        """
        Validate a version string without parsing
        
        Args:
            version_string: The version string to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            self.parse(version_string)
            return True
        except InvalidVersionError:
            return False
    
    def get_supported_patterns(self) -> List[str]:
        """Get list of supported version patterns"""
        return list(self._patterns.keys())
    
    def validate_module_name(self, module_name: str) -> None:
        """
        Validate module name according to rules
        
        Args:
            module_name: The module name to validate
            
        Raises:
            ValidationError: If the module name is invalid
        """
        if not module_name:
            raise ValidationError("module_name", module_name, "Module name cannot be empty")
        
        # Check pattern: alphanumeric start/end, allow hyphens, dots, underscores
        # For single character, just check if it's alphanumeric
        if len(module_name) == 1:
            if not module_name.isalnum():
                raise ValidationError(
                    "module_name", 
                    module_name, 
                    "Single character module name must be alphanumeric"
                )
        else:
            pattern = re.compile(r'^[a-zA-Z0-9][a-zA-Z0-9\-\._]*[a-zA-Z0-9]$')
            if not pattern.match(module_name):
                raise ValidationError(
                    "module_name", 
                    module_name, 
                    "Module name must start and end with alphanumeric characters, "
                    "and can contain hyphens, dots, and underscores"
                )
        
        # Additional validation rules
        if len(module_name) > 50:
            raise ValidationError("module_name", module_name, "Module name too long (max 50 chars)")
        
        # Check for consecutive special characters
        if '--' in module_name or '__' in module_name or '..' in module_name:
            raise ValidationError("module_name", module_name, "Consecutive special characters not allowed")
    
    def normalize_version(self, version_info: VersionInfo) -> VersionInfo:
        """
        Normalize version according to configuration
        
        Args:
            version_info: The version to normalize
            
        Returns:
            Normalized VersionInfo
        """
        normalized = VersionInfo(
            major=version_info.major,
            minor=version_info.minor,
            patch=version_info.patch,
            prefix=version_info.prefix or self.config.default_prefix,
            suffix=version_info.suffix or self.config.default_suffix,
            module=version_info.module
        )
        
        # Ensure version components match configured type
        if self.config.version_type == VersionType.MAJOR:
            normalized.minor = None
            normalized.patch = None
        elif self.config.version_type == VersionType.MAJOR_MINOR:
            normalized.patch = None
            if normalized.minor is None:
                normalized.minor = 0
        elif self.config.version_type == VersionType.SEMVER:
            if normalized.minor is None:
                normalized.minor = 0
            if normalized.patch is None:
                normalized.patch = 0
        
        return normalized
