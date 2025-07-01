"""
Git tag management and operations
"""

import subprocess
import shlex
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from ..models.tag import TagInfo, TagPattern, TagPatternRegistry
from ..models.version import VersionInfo
from ..exceptions import GitOperationError, TagNotFoundError
from ..core.version_parser import VersionParser
from ..utils.security import SecurityValidator


class TagManager:
    """Handles git tag operations and management"""
    
    def __init__(self, repo_path: str, version_parser: Optional[VersionParser] = None):
        self.repo_path = repo_path
        self.version_parser = version_parser or VersionParser()
        self.pattern_registry = TagPatternRegistry()
        self._tag_cache: Optional[List[str]] = None
        self._cache_timestamp: Optional[datetime] = None
        self._cache_ttl = timedelta(minutes=5)  # Cache expires after 5 minutes
        
    def get_all_tags(self, force_refresh: bool = False) -> List[str]:
        """
        Get all tags from the repository
        
        Args:
            force_refresh: Force refresh of tag cache
            
        Returns:
            List of tag names sorted by refname
            
        Raises:
            GitOperationError: If git operation fails
        """
        # Check if cache is expired
        cache_expired = (
            self._cache_timestamp is None or 
            datetime.now() - self._cache_timestamp > self._cache_ttl
        )
        
        if self._tag_cache is None or force_refresh or cache_expired:
            try:
                result = subprocess.run(
                    ['git', 'tag', '-l', '--sort=refname'],
                    cwd=self.repo_path,
                    capture_output=True,
                    text=True,
                    timeout=30,
                    check=True
                )
                tags = result.stdout.strip().split('\n') if result.stdout.strip() else []
                self._tag_cache = [tag.strip() for tag in tags if tag.strip()]
                self._cache_timestamp = datetime.now()
            except subprocess.TimeoutExpired:
                raise GitOperationError("get_all_tags", "Git command timed out")
            except subprocess.CalledProcessError as e:
                raise GitOperationError("get_all_tags", e.stderr, e.returncode)
            except Exception as e:
                raise GitOperationError("get_all_tags", str(e))
        
        return self._tag_cache.copy()
    
    def get_tags_matching_pattern(self, pattern: TagPattern) -> List[TagInfo]:
        """
        Get tags matching a specific pattern
        
        Args:
            pattern: TagPattern to match against
            
        Returns:
            List of TagInfo objects for matching tags
        """
        all_tags = self.get_all_tags()
        matching_tags = []
        
        for tag_name in all_tags:
            if pattern.matches(tag_name):
                try:
                    version_info = self.version_parser.parse(tag_name)
                    tag_info = TagInfo(name=tag_name, version_info=version_info)
                    matching_tags.append(tag_info)
                except Exception:
                    # Skip tags that can't be parsed
                    continue
        
        return sorted(matching_tags, key=lambda t: t.version_info)
    
    def get_latest_tag_for_pattern(self, pattern: TagPattern) -> Optional[TagInfo]:
        """
        Get the latest tag matching a pattern
        
        Args:
            pattern: TagPattern to match against
            
        Returns:
            Latest TagInfo or None if no matches found
        """
        matching_tags = self.get_tags_matching_pattern(pattern)
        return matching_tags[-1] if matching_tags else None
    
    def get_tags_for_module(self, module_name: str, version_file: str) -> List[TagInfo]:
        """
        Get all tags for a specific module
        
        Args:
            module_name: Name of the module
            version_file: Path to version file to determine version type
            
        Returns:
            List of TagInfo objects for the module
            
        Raises:
            TagNotFoundError: If no tags found for module
        """
        # Validate module name
        self.version_parser.validate_module_name(module_name)
        
        # Read version file to determine pattern type
        version_type = self._determine_version_type(version_file)
        
        # Create appropriate pattern for module
        if version_type == "semver":
            pattern = TagPattern.create_semver_pattern(module=module_name)
        elif version_type == "major_minor":
            pattern = TagPattern.create_major_minor_pattern(module=module_name)
        else:
            pattern = TagPattern.create_major_pattern(module=module_name)
        
        tags = self.get_tags_matching_pattern(pattern)
        if not tags:
            raise TagNotFoundError(module=module_name)
        
        return tags
    
    def get_tags_with_prefix(self, prefix: str, version_file: str) -> List[TagInfo]:
        """
        Get all tags with a specific prefix
        
        Args:
            prefix: Prefix to search for
            version_file: Path to version file to determine version type
            
        Returns:
            List of TagInfo objects with the prefix
        """
        version_type = self._determine_version_type(version_file)
        
        # Create appropriate pattern for prefix
        if version_type == "semver":
            pattern = TagPattern.create_semver_pattern(prefix=prefix)
        elif version_type == "major_minor":
            pattern = TagPattern.create_major_minor_pattern(prefix=prefix)
        else:
            pattern = TagPattern.create_major_pattern(prefix=prefix)
        
        return self.get_tags_matching_pattern(pattern)
    
    def get_tags_with_suffix(self, suffix: str, version_file: str) -> List[TagInfo]:
        """
        Get all tags with a specific suffix
        
        Args:
            suffix: Suffix to search for
            version_file: Path to version file to determine version type
            
        Returns:
            List of TagInfo objects with the suffix
        """
        version_type = self._determine_version_type(version_file)
        
        # Create appropriate pattern for suffix
        if version_type == "semver":
            pattern = TagPattern.create_semver_pattern(suffix=suffix)
        elif version_type == "major_minor":
            pattern = TagPattern.create_major_minor_pattern(suffix=suffix)
        else:
            pattern = TagPattern.create_major_pattern(suffix=suffix)
        
        return self.get_tags_matching_pattern(pattern)
    
    def get_plain_version_tags(self, version_file: str) -> List[TagInfo]:
        """
        Get all plain version tags (no prefix/suffix/module)
        
        Args:
            version_file: Path to version file to determine version type
            
        Returns:
            List of TagInfo objects for plain versions
        """
        version_type = self._determine_version_type(version_file)
        
        # Create appropriate pattern
        if version_type == "semver":
            pattern = TagPattern.create_semver_pattern()
        elif version_type == "major_minor":
            pattern = TagPattern.create_major_minor_pattern()
        else:
            pattern = TagPattern.create_major_pattern()
        
        return self.get_tags_matching_pattern(pattern)
    
    def create_tag(self, tag_name: str, message: str = None) -> bool:
        """
        Create a new git tag
        
        Args:
            tag_name: Name of the tag to create
            message: Optional tag message
            
        Returns:
            True if tag created successfully
            
        Raises:
            GitOperationError: If tag creation fails
        """
        try:
            cmd = ['git', 'tag']
            if message:
                cmd.extend(['-a', tag_name, '-m', message])
            else:
                cmd.append(tag_name)
            
            result = subprocess.run(
                cmd,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=30,
                check=True
            )
            
            # Clear cache to force refresh
            self._tag_cache = None
            return True
            
        except subprocess.TimeoutExpired:
            raise GitOperationError("create_tag", "Git command timed out")
        except subprocess.CalledProcessError as e:
            raise GitOperationError("create_tag", e.stderr, e.returncode)
    
    def tag_exists(self, tag_name: str) -> bool:
        """
        Check if a tag exists
        
        Args:
            tag_name: Name of the tag to check
            
        Returns:
            True if tag exists
        """
        all_tags = self.get_all_tags()
        return tag_name in all_tags
    
    def get_tag_info(self, tag_name: str) -> Optional[TagInfo]:
        """
        Get detailed information about a specific tag
        
        Args:
            tag_name: Name of the tag
            
        Returns:
            TagInfo object or None if tag doesn't exist
        """
        if not self.tag_exists(tag_name):
            return None
        
        try:
            # Get tag details
            result = subprocess.run(
                ['git', 'show', '--format=%H|%ci|%an|%s', '--no-patch', tag_name],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=30,
                check=True
            )
            
            parts = result.stdout.strip().split('|', 3)
            commit_hash = parts[0] if len(parts) > 0 else None
            created_date_str = parts[1] if len(parts) > 1 else None
            author = parts[2] if len(parts) > 2 else None
            message = parts[3] if len(parts) > 3 else None
            
            # Parse date
            created_date = None
            if created_date_str:
                try:
                    created_date = datetime.fromisoformat(created_date_str.replace(' ', 'T'))
                except ValueError:
                    pass
            
            # Parse version
            version_info = self.version_parser.parse(tag_name)
            
            return TagInfo(
                name=tag_name,
                version_info=version_info,
                commit_hash=commit_hash,
                created_date=created_date,
                author=author,
                message=message
            )
            
        except Exception:
            # Fallback to basic info
            try:
                version_info = self.version_parser.parse(tag_name)
                return TagInfo(name=tag_name, version_info=version_info)
            except Exception:
                return None
    
    def _determine_version_type(self, version_file: str) -> str:
        """
        Determine version type from version file content
        
        Args:
            version_file: Path to version file
            
        Returns:
            Version type: 'semver', 'major_minor', or 'major'
        """
        try:
            # Validate file path for security
            safe_path = SecurityValidator.validate_file_path(version_file, self.repo_path)
            
            with open(safe_path, 'r') as f:
                content = f.read().strip()
            
            if '.' in content:
                parts = content.split('.')
                if len(parts) >= 3:
                    return "semver"
                elif len(parts) == 2:
                    return "major_minor"
            
            return "major"
            
        except Exception:
            # Default to semver if can't read file
            return "semver"
    
    def clear_cache(self) -> None:
        """Clear the tag cache"""
        self._tag_cache = None
        self._cache_timestamp = None
    
    def set_cache_ttl(self, ttl_minutes: int) -> None:
        """Set cache time-to-live in minutes"""
        self._cache_ttl = timedelta(minutes=ttl_minutes)
