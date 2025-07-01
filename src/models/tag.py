"""
Tag data models and utilities
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional, Pattern, TYPE_CHECKING
from datetime import datetime
import re

if TYPE_CHECKING:
    from .version import VersionInfo


@dataclass
class TagInfo:
    """Represents a git tag with parsed information"""
    name: str
    version_info: VersionInfo
    commit_hash: Optional[str] = None
    created_date: Optional[datetime] = None
    author: Optional[str] = None
    message: Optional[str] = None
    
    def __str__(self) -> str:
        return self.name
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, TagInfo):
            return False
        return self.name == other.name
    
    def __lt__(self, other) -> bool:
        """Compare tags by version for sorting"""
        if not isinstance(other, TagInfo):
            return NotImplemented
        return self.version_info < other.version_info


@dataclass
class TagPattern:
    """Represents a tag pattern for matching and filtering"""
    name: str
    pattern: Pattern[str]
    prefix: Optional[str] = None
    suffix: Optional[str] = None
    module: Optional[str] = None
    description: Optional[str] = None
    
    def matches(self, tag_name: str) -> bool:
        """Check if a tag name matches this pattern"""
        return bool(self.pattern.match(tag_name))
    
    def extract_version(self, tag_name: str) -> Optional[str]:
        """Extract version string from tag name"""
        match = self.pattern.match(tag_name)
        if not match:
            return None
        
        # Assume the version is in the first capture group
        groups = match.groups()
        return groups[0] if groups else None
    
    @classmethod
    def create_semver_pattern(cls, prefix: str = None, suffix: str = None, module: str = None) -> 'TagPattern':
        """Create a pattern for semantic versioning"""
        version_regex = r'(\d+\.\d+\.\d+)'
        
        if module:
            pattern_str = f'^{re.escape(module)}-{version_regex}$'
            name = f"module-{module}"
        elif prefix:
            pattern_str = f'^{re.escape(prefix)}-{version_regex}$'
            name = f"prefix-{prefix}"
        elif suffix:
            pattern_str = f'^{version_regex}-{re.escape(suffix)}$'
            name = f"suffix-{suffix}"
        else:
            pattern_str = f'^{version_regex}$'
            name = "plain-semver"
        
        return cls(
            name=name,
            pattern=re.compile(pattern_str),
            prefix=prefix,
            suffix=suffix,
            module=module,
            description=f"Semantic version pattern: {pattern_str}"
        )
    
    @classmethod
    def create_major_minor_pattern(cls, prefix: str = None, suffix: str = None, module: str = None) -> 'TagPattern':
        """Create a pattern for major.minor versioning"""
        version_regex = r'(\d+\.\d+)'
        
        if module:
            pattern_str = f'^{re.escape(module)}-{version_regex}$'
            name = f"module-{module}-major-minor"
        elif prefix:
            pattern_str = f'^{re.escape(prefix)}-{version_regex}$'
            name = f"prefix-{prefix}-major-minor"
        elif suffix:
            pattern_str = f'^{version_regex}-{re.escape(suffix)}$'
            name = f"suffix-{suffix}-major-minor"
        else:
            pattern_str = f'^{version_regex}$'
            name = "plain-major-minor"
        
        return cls(
            name=name,
            pattern=re.compile(pattern_str),
            prefix=prefix,
            suffix=suffix,
            module=module,
            description=f"Major.minor version pattern: {pattern_str}"
        )
    
    @classmethod
    def create_major_pattern(cls, prefix: str = None, suffix: str = None, module: str = None) -> 'TagPattern':
        """Create a pattern for major versioning"""
        version_regex = r'(\d+)'
        
        if module:
            pattern_str = f'^{re.escape(module)}-{version_regex}$'
            name = f"module-{module}-major"
        elif prefix:
            pattern_str = f'^{re.escape(prefix)}-{version_regex}$'
            name = f"prefix-{prefix}-major"
        elif suffix:
            pattern_str = f'^{version_regex}-{re.escape(suffix)}$'
            name = f"suffix-{suffix}-major"
        else:
            pattern_str = f'^{version_regex}$'
            name = "plain-major"
        
        return cls(
            name=name,
            pattern=re.compile(pattern_str),
            prefix=prefix,
            suffix=suffix,
            module=module,
            description=f"Major version pattern: {pattern_str}"
        )


class TagPatternRegistry:
    """Registry for managing tag patterns"""
    
    def __init__(self):
        self.patterns: List[TagPattern] = []
    
    def add_pattern(self, pattern: TagPattern) -> None:
        """Add a pattern to the registry"""
        self.patterns.append(pattern)
    
    def remove_pattern(self, name: str) -> bool:
        """Remove a pattern by name"""
        for i, pattern in enumerate(self.patterns):
            if pattern.name == name:
                del self.patterns[i]
                return True
        return False
    
    def get_pattern(self, name: str) -> Optional[TagPattern]:
        """Get a pattern by name"""
        for pattern in self.patterns:
            if pattern.name == name:
                return pattern
        return None
    
    def find_matching_patterns(self, tag_name: str) -> List[TagPattern]:
        """Find all patterns that match a tag name"""
        return [pattern for pattern in self.patterns if pattern.matches(tag_name)]
    
    def clear(self) -> None:
        """Clear all patterns"""
        self.patterns.clear()
