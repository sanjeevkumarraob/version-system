"""
Main entry point for the improved Version System
"""

import argparse
import os
import sys
from typing import Optional
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.core.version_parser import VersionParser
from src.core.tag_manager import TagManager
from src.core.version_calculator import VersionCalculator
from src.models.version import VersionConfig, IncrementType
from src.exceptions import VersionSystemError
from src.utils.utils import get_logger
from src.utils.config_loader import ConfigLoader
from src.utils.security import SecurityValidator


class VersionSystem:
    """Main class orchestrating version system operations"""
    
    def __init__(self, repo_path: str, version_file: str, config: Optional[VersionConfig] = None):
        # Validate and secure paths
        self.repo_path = SecurityValidator.validate_directory_path(repo_path)
        self.version_file = version_file  # Will be validated when used
        self.config = config or VersionConfig()
        self.logger = get_logger()
        
        # Initialize components
        self.version_parser = VersionParser(self.config)
        self.tag_manager = TagManager(self.repo_path, self.version_parser)
        self.version_calculator = VersionCalculator(self.config)
    
    def process_version_request(
        self,
        prefix: Optional[str] = None,
        suffix: Optional[str] = None,
        module: Optional[str] = None,
        branch: Optional[str] = None,
        is_snapshot: bool = False
    ) -> str:
        """
        Process a version request and return the next version
        
        Args:
            prefix: Version prefix
            suffix: Version suffix
            module: Module name
            branch: Branch name for snapshots
            is_snapshot: Whether to create snapshot version
            
        Returns:
            Next version string
            
        Raises:
            VersionSystemError: If processing fails
        """
        try:
            self.logger.info(f"Processing version request: prefix={prefix}, suffix={suffix}, "
                           f"module={module}, branch={branch}, is_snapshot={is_snapshot}")
            
            # Validate inputs
            self._validate_inputs(prefix, suffix, module)
            
            # Read base version from file
            base_version = self._read_base_version()
            self.logger.info(f"Base version from file: {base_version}")
            
            # Get current version from tags
            current_version = self._get_current_version(prefix, suffix, module)
            self.logger.info(f"Current version from tags: {current_version}")
            
            # Calculate next version
            next_version = self.version_calculator.calculate_next_version(
                current_version, base_version
            )
            
            # Apply prefix, suffix, or module to the calculated version
            if prefix:
                # Remove trailing dash from prefix if present
                clean_prefix = prefix.rstrip('-')
                next_version.prefix = clean_prefix
            elif suffix:
                # Remove leading dash from suffix if present
                clean_suffix = suffix.lstrip('-')
                next_version.suffix = clean_suffix
            elif module:
                next_version.module = module
            
            # Handle snapshot versions
            if is_snapshot:
                next_version = self.version_calculator.create_snapshot_version(
                    next_version, branch
                )
            
            result = str(next_version)
            self.logger.info(f"Next version: {result}")
            
            # Set GitHub outputs
            self._set_github_output("next_tag", result)
            if current_version:
                self._set_github_output("current_tag", str(current_version))
            
            return result
            
        except VersionSystemError:
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
            raise VersionSystemError(f"Processing failed: {str(e)}")
    
    def _validate_inputs(self, prefix: Optional[str], suffix: Optional[str], module: Optional[str]):
        """Validate input parameters"""
        # Check for reserved keywords
        reserved_keywords = ['SNAPSHOT']
        
        if prefix and prefix.upper() in reserved_keywords:
            raise VersionSystemError(f"'{prefix}' is a reserved keyword and cannot be used as prefix")
        
        if suffix and suffix.upper() in reserved_keywords:
            raise VersionSystemError(f"'{suffix}' is a reserved keyword and cannot be used as suffix")
        
        # Validate module name if provided
        if module:
            self.version_parser.validate_module_name(module)
        
        # Check that only one of prefix/suffix/module is specified
        specified_options = sum(1 for x in [prefix, suffix, module] if x is not None)
        if specified_options > 1:
            raise VersionSystemError("Only one of prefix, suffix, or module can be specified")
    
    def _read_base_version(self):
        """Read and parse base version from version file"""
        try:
            # Validate file path for security
            version_path = SecurityValidator.validate_file_path(
                os.path.join(self.repo_path, self.version_file), 
                self.repo_path
            )
            
            with open(version_path, 'r') as f:
                content = f.read().strip()
            
            if not content:
                raise VersionSystemError("Version file is empty")
            
            # Parse as plain version (no prefix/suffix/module)
            base_version = self.version_parser.parse(content)
            
            # Auto-adjust configuration based on detected version type
            self._auto_adjust_config_for_version_type(base_version)
            
            return base_version
            
        except FileNotFoundError:
            raise VersionSystemError(f"Version file not found: {self.version_file}")
        except Exception as e:
            raise VersionSystemError(f"Failed to read version file: {str(e)}")
    
    def _auto_adjust_config_for_version_type(self, version):
        """Auto-adjust configuration based on detected version type"""
        # If version is major.minor (like 3.0), adjust increment type to minor
        if version.version_type.value == "major_minor" and self.version_calculator.config.increment_type.value == "patch":
            from src.models.version import VersionConfig, IncrementType
            # Create new config with minor increment for major.minor versions
            new_config = VersionConfig(
                version_type=self.version_calculator.config.version_type,
                increment_type=IncrementType.MINOR,  # Change to minor for major.minor versions
                allow_prerelease=self.version_calculator.config.allow_prerelease,
                default_prefix=self.version_calculator.config.default_prefix,
                default_suffix=self.version_calculator.config.default_suffix
            )
            self.version_calculator.config = new_config
            self.logger.info(f"Auto-adjusted increment type to 'minor' for major.minor version format")
    
    def _get_current_version(self, prefix: Optional[str], suffix: Optional[str], module: Optional[str]):
        """Get current version from git tags"""
        try:
            if module:
                tags = self.tag_manager.get_tags_for_module(module, 
                    os.path.join(self.repo_path, self.version_file))
            elif prefix:
                tags = self.tag_manager.get_tags_with_prefix(prefix,
                    os.path.join(self.repo_path, self.version_file))
            elif suffix:
                # Filter out snapshot tags for suffix
                all_tags = self.tag_manager.get_tags_with_suffix(suffix,
                    os.path.join(self.repo_path, self.version_file))
                tags = [tag for tag in all_tags if 'SNAPSHOT' not in tag.name]
            else:
                tags = self.tag_manager.get_plain_version_tags(
                    os.path.join(self.repo_path, self.version_file))
            
            if not tags:
                self.logger.info("No existing tags found")
                return None
            
            # Return the latest version
            latest_tag = max(tags, key=lambda t: t.version_info)
            return latest_tag.version_info
            
        except Exception as e:
            self.logger.warning(f"Failed to get current version from tags: {str(e)}")
            return None
    
    def _set_github_output(self, name: str, value: str):
        """Set GitHub Actions output variable"""
        github_output = os.environ.get('GITHUB_OUTPUT')
        if github_output:
            try:
                with open(github_output, 'a') as f:
                    f.write(f'{name}={value}\n')
            except Exception as e:
                self.logger.warning(f"Failed to set GitHub output {name}: {e}")


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(description='Version System - Improved')
    
    parser.add_argument('-p', '--prefix', dest='prefix', 
                       help='Prefix for the tag (e.g., dev-1.0.0)')
    parser.add_argument('-s', '--suffix', dest='suffix',
                       help='Suffix for the tag (e.g., 1.0.0-rc)')
    parser.add_argument('-m', '--module', dest='module',
                       help='Module name for the tag (e.g., alpine-1.0.0)')
    parser.add_argument('-b', '--branch', dest='branch',
                       help='Branch name for snapshot versions')
    parser.add_argument('-f', '--version-file', dest='version_file', required=True,
                       help='Path to version file')
    parser.add_argument('-r', '--git-repo-path', dest='git_repo_path', required=True,
                       help='Path to git repository')
    parser.add_argument('-i', '--is-snapshot', dest='is_snapshot', action='store_true',
                       help='Create snapshot version')
    parser.add_argument('--config', dest='config_file',
                       help='Path to configuration file')
    
    args = parser.parse_args()
    
    try:
        # Load configuration if provided
        config = None
        if args.config_file:
            try:
                config = ConfigLoader.load_config(args.config_file)
                print(f"Loaded configuration from: {args.config_file}")
            except Exception as e:
                print(f"Warning: Failed to load config file: {e}", file=sys.stderr)
                print("Using default configuration", file=sys.stderr)
        
        # Initialize version system
        version_system = VersionSystem(
            repo_path=args.git_repo_path,
            version_file=args.version_file,
            config=config
        )
        
        # Process version request
        result = version_system.process_version_request(
            prefix=args.prefix,
            suffix=args.suffix,
            module=args.module,
            branch=args.branch,
            is_snapshot=args.is_snapshot
        )
        
        print(f"Next version: {result}")
        return 0
        
    except VersionSystemError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
