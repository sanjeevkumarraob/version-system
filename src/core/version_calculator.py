"""
Version calculation and increment logic
"""

from typing import Optional
from ..models.version import VersionInfo, IncrementType, VersionType, VersionConfig
from ..models.tag import TagInfo
from ..exceptions import InvalidVersionError, ConfigurationError


class VersionCalculator:
    """Handles version calculation and increment operations"""
    
    def __init__(self, config: Optional[VersionConfig] = None):
        self.config = config or VersionConfig()
    
    def calculate_next_version(
        self, 
        current_version: Optional[VersionInfo], 
        base_version: VersionInfo,
        increment_type: Optional[IncrementType] = None
    ) -> VersionInfo:
        """
        Calculate the next version based on current version and base version
        
        Args:
            current_version: Current latest version (from tags)
            base_version: Base version from version file
            increment_type: How to increment the version
            
        Returns:
            Next version to use
            
        Raises:
            InvalidVersionError: If version calculation fails
            ConfigurationError: If configuration is invalid
        """
        # Validate increment_type
        increment_type = increment_type or self.config.increment_type
        if not isinstance(increment_type, IncrementType):
            raise ConfigurationError("increment_type", f"Invalid increment type: {increment_type}")
        
        # Validate base_version
        if not isinstance(base_version, VersionInfo):
            raise InvalidVersionError(str(base_version), "Base version must be a VersionInfo object")
        
        if current_version is None:
            # No existing versions, use base version
            return self._normalize_version(base_version)
        
        # Validate current_version
        if not isinstance(current_version, VersionInfo):
            raise InvalidVersionError(str(current_version), "Current version must be a VersionInfo object")
        
        # Determine which version to increment from
        version_to_increment = self._select_version_to_increment(current_version, base_version)
        
        # Perform increment
        try:
            next_version = version_to_increment.increment(increment_type)
            return self._normalize_version(next_version)
        except ValueError as e:
            raise InvalidVersionError(str(version_to_increment), str(e))
    
    def _select_version_to_increment(
        self, 
        current_version: VersionInfo, 
        base_version: VersionInfo
    ) -> VersionInfo:
        """
        Select which version to increment based on comparison
        
        Args:
            current_version: Current version from tags
            base_version: Base version from version file
            
        Returns:
            Version to increment
        """
        # Compare major versions first
        if base_version.major > current_version.major:
            # Base version has higher major, use base version
            return base_version
        elif base_version.major < current_version.major:
            # Current version has higher major, increment current
            return current_version
        
        # Major versions are equal, check minor
        base_minor = base_version.minor or 0
        current_minor = current_version.minor or 0
        
        if base_minor > current_minor:
            # Base version has higher minor, use base version
            return base_version
        elif base_minor < current_minor:
            # Current version has higher minor, increment current
            return current_version
        
        # Major and minor are equal, check patch
        base_patch = base_version.patch or 0
        current_patch = current_version.patch or 0
        
        if base_patch > current_patch:
            # Base version has higher patch, use base version
            return base_version
        else:
            # Current version is >= base patch, increment current
            return current_version
    
    def _normalize_version(self, version: VersionInfo) -> VersionInfo:
        """
        Normalize version according to configuration
        
        Args:
            version: Version to normalize
            
        Returns:
            Normalized version
        """
        normalized = VersionInfo(
            major=version.major,
            minor=version.minor,
            patch=version.patch,
            prefix=version.prefix,
            suffix=version.suffix,
            module=version.module
        )
        
        # Apply configuration defaults
        if self.config.default_prefix and not normalized.prefix:
            normalized.prefix = self.config.default_prefix
        if self.config.default_suffix and not normalized.suffix:
            normalized.suffix = self.config.default_suffix
        
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
    
    def compare_versions(self, version1: VersionInfo, version2: VersionInfo) -> int:
        """
        Compare two versions
        
        Args:
            version1: First version
            version2: Second version
            
        Returns:
            -1 if version1 < version2, 0 if equal, 1 if version1 > version2
        """
        if version1 < version2:
            return -1
        elif version1 == version2:
            return 0
        else:
            return 1
    
    def is_version_compatible(self, version: VersionInfo, base_version: VersionInfo) -> bool:
        """
        Check if a version is compatible with the base version
        
        Args:
            version: Version to check
            base_version: Base version to compare against
            
        Returns:
            True if compatible
        """
        # Check major version compatibility
        if version.major < base_version.major:
            return False
        
        # If major versions are equal, check minor
        if version.major == base_version.major:
            base_minor = base_version.minor or 0
            version_minor = version.minor or 0
            
            if version_minor < base_minor:
                return False
            
            # If minor versions are equal, check patch
            if version_minor == base_minor:
                base_patch = base_version.patch or 0
                version_patch = version.patch or 0
                
                if version_patch < base_patch:
                    return False
        
        return True
    
    def create_snapshot_version(
        self, 
        base_version: VersionInfo, 
        branch_name: Optional[str] = None
    ) -> VersionInfo:
        """
        Create a snapshot version
        
        Args:
            base_version: Base version to create snapshot from
            branch_name: Optional branch name to include
            
        Returns:
            Snapshot version
        """
        snapshot_version = VersionInfo(
            major=base_version.major,
            minor=base_version.minor,
            patch=base_version.patch,
            prefix=base_version.prefix,
            suffix="SNAPSHOT",
            module=base_version.module
        )
        
        # If branch name provided, include it in suffix
        if branch_name:
            # Clean branch name for tag usage
            clean_branch = branch_name.replace("/", "-")[:20]
            snapshot_version.suffix = f"{clean_branch}-SNAPSHOT"
        
        return snapshot_version
    
    def get_version_increment_suggestions(self, current_version: VersionInfo) -> dict:
        """
        Get suggestions for version increments
        
        Args:
            current_version: Current version
            
        Returns:
            Dictionary with increment suggestions
        """
        suggestions = {}
        
        try:
            suggestions['patch'] = current_version.increment(IncrementType.PATCH)
        except ValueError:
            pass
        
        try:
            suggestions['minor'] = current_version.increment(IncrementType.MINOR)
        except ValueError:
            pass
        
        try:
            suggestions['major'] = current_version.increment(IncrementType.MAJOR)
        except ValueError:
            pass
        
        return suggestions
