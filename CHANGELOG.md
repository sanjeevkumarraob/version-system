# Changelog

All notable changes to the Version System will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial public release preparation

## [1.0.0] - 2025-01-01

### Added
- 🚀 **Automated semantic versioning** for GitHub Actions
- 🔧 **Flexible configuration** with support for prefixes, suffixes, and modules
- 📦 **Module-specific versioning** for monorepo support
- 🧪 **Comprehensive test suite** with 97% coverage
- 🔒 **Security validations** and path traversal protection
- 🐳 **Docker support** for containerized environments
- 📋 **GitHub Actions integration** with easy setup
- 🏷️ **Multiple version formats** support (semver, major.minor, major)
- ⚡ **High performance** version calculation algorithms
- 📚 **Complete documentation** with usage examples

### Features
- Automatic version generation based on existing tags
- Support for version prefixes (e.g., `dev-1.0.0`)
- Support for version suffixes (e.g., `1.0.0-beta`)
- Module-specific tagging (e.g., `api-1.0.0`, `cli-2.1.0`)
- Intelligent version increment detection
- Branch-based snapshot versioning
- Release creation with automated release notes
- Path traversal security protection
- Comprehensive error handling and validation

### Technical Details
- Python 3.10+ support
- Docker containerization
- GitHub Actions integration
- Extensive unit and integration testing
- Security-first design principles
- Clean, maintainable codebase

---

## Release Process

This project uses automated releases:

1. **Version Bump**: Use the "Version Bump and Tag" workflow to create new versions
2. **Automatic Release**: Pushing a version tag triggers the release workflow
3. **Major Version Tags**: Major version tags (v1, v2, etc.) are automatically updated

### Version Tag Examples
- `v1.0.0` - Initial release
- `v1.1.0` - Minor feature addition
- `v1.1.1` - Patch/bug fix
- `v2.0.0` - Major version with breaking changes

### Usage Tags
Users reference the action using major version tags:
- `sanjeevkumarraob/version-system@v1` - Latest v1.x.x
- `sanjeevkumarraob/version-system@v2` - Future v2.x.x (when available)
