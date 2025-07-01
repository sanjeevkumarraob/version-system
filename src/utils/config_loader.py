"""
Configuration loading utilities
"""

import yaml
import os
from typing import Optional, Dict, Any
from pathlib import Path
from ..models.version import VersionConfig, VersionType, IncrementType
from ..exceptions import ConfigurationError


class ConfigLoader:
    """Handles loading and parsing of configuration files"""
    
    @staticmethod
    def load_config(config_path: str) -> VersionConfig:
        """
        Load configuration from YAML file
        
        Args:
            config_path: Path to configuration file
            
        Returns:
            VersionConfig object
            
        Raises:
            ConfigurationError: If config loading fails
        """
        if not os.path.exists(config_path):
            raise ConfigurationError("config_file", f"Configuration file not found: {config_path}")
        
        try:
            with open(config_path, 'r') as f:
                config_data = yaml.safe_load(f)
            
            if not config_data:
                raise ConfigurationError("config_file", "Configuration file is empty")
            
            # Extract version config section
            version_config_data = config_data.get('version_config', {})
            
            return ConfigLoader._parse_version_config(version_config_data)
            
        except yaml.YAMLError as e:
            raise ConfigurationError("config_file", f"Invalid YAML format: {str(e)}")
        except Exception as e:
            raise ConfigurationError("config_file", f"Failed to load configuration: {str(e)}")
    
    @staticmethod
    def _parse_version_config(config_data: Dict[str, Any]) -> VersionConfig:
        """Parse version configuration from dictionary"""
        try:
            # Parse version type
            version_type_str = config_data.get('version_type', 'semver')
            try:
                version_type = VersionType(version_type_str)
            except ValueError:
                raise ConfigurationError("version_type", f"Invalid version type: {version_type_str}")
            
            # Parse increment type
            increment_type_str = config_data.get('increment_type', 'patch')
            try:
                increment_type = IncrementType(increment_type_str)
            except ValueError:
                raise ConfigurationError("increment_type", f"Invalid increment type: {increment_type_str}")
            
            # Parse other options
            allow_prerelease = config_data.get('allow_prerelease', False)
            default_prefix = config_data.get('default_prefix')
            default_suffix = config_data.get('default_suffix')
            
            # Validate string values
            if default_prefix and not isinstance(default_prefix, str):
                raise ConfigurationError("default_prefix", "Must be a string")
            if default_suffix and not isinstance(default_suffix, str):
                raise ConfigurationError("default_suffix", "Must be a string")
            
            return VersionConfig(
                version_type=version_type,
                increment_type=increment_type,
                allow_prerelease=allow_prerelease,
                default_prefix=default_prefix,
                default_suffix=default_suffix
            )
            
        except ConfigurationError:
            raise
        except Exception as e:
            raise ConfigurationError("version_config", f"Invalid configuration format: {str(e)}")
    
    @staticmethod
    def create_default_config(config_path: str) -> None:
        """Create a default configuration file"""
        default_config = {
            'version_config': {
                'version_type': 'semver',
                'increment_type': 'patch',
                'allow_prerelease': False,
                'default_prefix': None,
                'default_suffix': None
            },
            'modules': [
                {
                    'name': 'example-module',
                    'path': 'src/module',
                    'version_file': 'version.txt'
                }
            ]
        }
        
        try:
            with open(config_path, 'w') as f:
                yaml.dump(default_config, f, default_flow_style=False, indent=2)
        except Exception as e:
            raise ConfigurationError("config_creation", f"Failed to create config file: {str(e)}")
