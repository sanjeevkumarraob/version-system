# Contributing to Version System

Thank you for your interest in contributing to the Version System! This document provides guidelines for contributing to this project.

## Getting Started

1. Fork the repository
2. Clone your fork locally
3. Create a new branch for your feature or bug fix
4. Make your changes
5. Test your changes
6. Submit a pull request

## Development Setup

```bash
# Clone your fork
git clone https://github.com/sanjeevkumarraob/version-system.git
cd version-system

# Install dependencies
pip install -r requirements.txt

# Run tests
make run_test
# or
./run_tests.sh all
```

## Testing

Before submitting a pull request, ensure:

- All existing tests pass
- New functionality includes appropriate tests
- Test coverage remains high

```bash
# Run all tests
./run_tests.sh all

# Run specific test types
./run_tests.sh unit
./run_tests.sh coverage
```

## Code Style

- Follow Python PEP 8 guidelines
- Use meaningful variable and function names
- Add docstrings for new functions and classes
- Keep functions focused and concise

## Submitting Changes

1. **Create a descriptive commit message**
   ```
   Add support for custom version patterns
   
   - Implement regex-based version pattern matching
   - Add tests for new pattern functionality
   - Update documentation with examples
   ```

2. **Push to your fork and submit a pull request**

3. **Describe your changes** in the pull request description

## Types of Contributions

We welcome:

- **Bug fixes** - Fix issues or improve error handling
- **New features** - Add new versioning capabilities
- **Documentation** - Improve README, add examples
- **Tests** - Increase test coverage or add edge cases
- **Performance** - Optimize existing functionality

## Questions?

If you have questions about contributing, please:

1. Check existing issues and discussions
2. Open a new issue with the "question" label
3. Be specific about what you're trying to achieve

## Code of Conduct

Please be respectful and constructive in all interactions. We're here to build something useful together!

Thank you for contributing! 🚀
