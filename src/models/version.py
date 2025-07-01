"""
Version data models and utilities
"""

from dataclasses import dataclass
from typing import Optional, Tuple
from enum import Enum


class VersionType(Enum):
    """Supported version types"""
    MAJOR = "major"
    MAJOR_MINOR = "major_minor"
    SEMVER = "semver"


class IncrementType(Enum):
    """Version increment types"""
    MAJOR = "major"
    MINOR = "minor"
    PATCH = "patch"


@dataclass
class VersionInfo:
    """Represents a parsed version"""
    major: int
    minor: Optional[int] = None
    patch: Optional[int] = None
    prefix: Optional[str] = None
    suffix: Optional[str] = None
    module: Optional[str] = None
    
    @property
    def version_type(self) -> VersionType:
        """Determine the version type based on available components"""
        if self.patch is not None:
            return VersionType.SEMVER
        elif self.minor is not None:
            return VersionType.MAJOR_MINOR
        else:
            return VersionType.MAJOR
    
    @property
    def base_version(self) -> str:
        """Get the base version string without prefix/suffix"""
        if self.version_type == VersionType.SEMVER:
            return f"{self.major}.{self.minor}.{self.patch}"
        elif self.version_type == VersionType.MAJOR_MINOR:
            return f"{self.major}.{self.minor}"
        else:
            return str(self.major)
    
    @property
    def full_version(self) -> str:
        """Get the full version string with prefix/suffix"""
        version = self.base_version
        
        if self.module:
            version = f"{self.module}-{version}"
        elif self.prefix:
            version = f"{self.prefix}-{version}"
        
        if self.suffix:
            version = f"{version}-{self.suffix}"
        
        return version
    
    def increment(self, increment_type: IncrementType) -> 'VersionInfo':
        """Create a new VersionInfo with incremented version"""
        new_version = VersionInfo(
            major=self.major,
            minor=self.minor,
            patch=self.patch,
            prefix=self.prefix,
            suffix=self.suffix,
            module=self.module
        )
        
        if increment_type == IncrementType.MAJOR:
            new_version.major += 1
            if new_version.minor is not None:
                new_version.minor = 0
            if new_version.patch is not None:
                new_version.patch = 0
        elif increment_type == IncrementType.MINOR:
            if new_version.minor is not None:
                new_version.minor += 1
                if new_version.patch is not None:
                    new_version.patch = 0
            else:
                raise ValueError("Cannot increment minor version for major-only version")
        elif increment_type == IncrementType.PATCH:
            if new_version.patch is not None:
                new_version.patch += 1
            else:
                raise ValueError("Cannot increment patch version for non-semver version")
        
        return new_version
    
    def __str__(self) -> str:
        return self.full_version
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, VersionInfo):
            return False
        return (
            self.major == other.major and
            self.minor == other.minor and
            self.patch == other.patch and
            self.prefix == other.prefix and
            self.suffix == other.suffix and
            self.module == other.module
        )
    
    def __hash__(self) -> int:
        """Make VersionInfo hashable for use in sets/dicts"""
        return hash((
            self.major,
            self.minor,
            self.patch,
            self.prefix,
            self.suffix,
            self.module
        ))
    
    def __lt__(self, other) -> bool:
        """Compare versions for sorting"""
        if not isinstance(other, VersionInfo):
            return NotImplemented
        
        # First compare by module/prefix (for grouping)
        self_identifier = self.module or self.prefix or ""
        other_identifier = other.module or other.prefix or ""
        
        if self_identifier != other_identifier:
            return self_identifier < other_identifier
        
        # Then compare major version
        if self.major != other.major:
            return self.major < other.major
        
        # Compare minor version
        self_minor = self.minor or 0
        other_minor = other.minor or 0
        if self_minor != other_minor:
            return self_minor < other_minor
        
        # Compare patch version
        self_patch = self.patch or 0
        other_patch = other.patch or 0
        if self_patch != other_patch:
            return self_patch < other_patch
        
        # Finally compare suffix (for pre-release ordering)
        self_suffix = self.suffix or ""
        other_suffix = other.suffix or ""
        
        # Handle special case: versions without suffix come after those with suffix
        # e.g., 1.0.0 > 1.0.0-beta
        if self_suffix and not other_suffix:
            return True
        elif not self_suffix and other_suffix:
            return False
        
        return self_suffix < other_suffix


@dataclass
class VersionConfig:
    """Configuration for version parsing and generation"""
    version_type: VersionType = VersionType.SEMVER  # Reverted to original default
    increment_type: IncrementType = IncrementType.PATCH  # Reverted to original default
    allow_prerelease: bool = False
    default_prefix: Optional[str] = None
    default_suffix: Optional[str] = None
    
    @classmethod
    def from_dict(cls, config_dict: dict) -> 'VersionConfig':
        """Create VersionConfig from dictionary"""
        return cls(
            version_type=VersionType(config_dict.get('version_type', 'semver')),
            increment_type=IncrementType(config_dict.get('increment_type', 'patch')),
            allow_prerelease=config_dict.get('allow_prerelease', False),
            default_prefix=config_dict.get('default_prefix'),
            default_suffix=config_dict.get('default_suffix')
        )
