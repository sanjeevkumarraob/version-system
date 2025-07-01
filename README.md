# Versioning System

This GitHub Action checks the latest tag available for the repository and outputs the next tag to be used for automated semantic versioning.

## Features

- 🏷️ **Automatic Version Generation**: Generates next semantic version based on existing tags
- 🔧 **Flexible Configuration**: Support for prefixes, suffixes, and module-specific versioning
- 📦 **Module Support**: Create separate version tags for different modules in a monorepo
- 🚀 **GitHub Actions Integration**: Easy integration with CI/CD workflows
- 🧪 **Well Tested**: 97% test coverage with comprehensive test suite
- 🔒 **Secure**: Built-in security validations and path traversal protection

## Pre-Requisite

Please update your checkout step with fetch-depth flag. This way, the tags are pulled as part of checkout.

```yaml
- name: checkout repo
  uses: actions/checkout@v4
  with:
    fetch-depth: 0
    clean: true
```

## Inputs

### `PREFIX`

Prefix for the tag eg., dev-1.0.0. If you need a tag with a prefix, use this option.

Enabling this option will look for the latest tag for this prefix and creates the next tag. If there are no tags available for the prefix, it will create a new tag based on the version file.

### `SUFFIX`

Suffix for the tag eg., 1.0.0-beta. If you need a tag with a suffix, use this option.

Enabling this option will look for the latest tag for this suffix and creates the next tag. If there are no tags available for the suffix, it will create a new tag based on the version file.

### `MODULE`

Module for the tag eg., alpine-1.0.0 or my_cli-1.0.0. If you need to create a tag for a module inside the repo, use this option.

Module names can contain:
- Alphanumeric characters (a-z, A-Z, 0-9)
- Hyphens (-)
- Underscores (_)
- Dots (.)

Must start and end with an alphanumeric character.

Examples of valid module names:
- my_cli
- my-module
- api.gateway
- test_api-v2
- my_cli-1.0.0

Enabling this option will look for the latest tag for this module and creates the next tag. If there are no tags available for the module, it will create a new tag based on the version file.

```
.
├── module1
│   ├── Dockerfile
│   ├── version.txt (can contain 2.3.0) - output can be alpine-2.3.5 or my_cli-2.3.5
│   └── src
├── module2
│   ├── Dockerfile
│   ├── version.txt (can contain 1.0.0)
│   └── src
├── files_in_root
└── README.md
```

### `VERSION_FILE`

**Required**  Path for the version.txt file. This file must be present and the versions will be created based on this file. If you are following version.txt per module, then change the version path accordingly.

### `GIT_REPO_PATH`

**Required**  Path for the git repo. This repo will be used to get the tags.

### `CREATE_RELEASE`

If you want to create a tag and a github release along with release notes as part of the pipeline, set this flag as true.

## Update Base Version

If you want to create a new version, eg., from `1.9.0` to `2.0.0`, update the version.txt file to the new base version. Based on this new version, corresponding versions will be created.

## Outputs

### `VERSION`

This action will set a `$GITHUB_OUTPUT` variable in `version`. You can use this output variable and create a tag or release in your pipeline.

### `CURRENT_VERSION`

This action will set a `$GITHUB_OUTPUT` variable in `current_version`. This is the last available tag for the repository.

## Example usage

### With a dev prefix

```yaml
uses: sanjeevkumarraob/version-system@v1
with:
  PREFIX: 'dev-'
  VERSION_FILE: "version.txt"
```

### With a snapshot suffix

```yaml
uses: sanjeevkumarraob/version-system@v1
with:
  SUFFIX: 'snapshot'
  VERSION_FILE: "version.txt"
```

### TAG for a module

```yaml
# Using hyphen
uses: sanjeevkumarraob/version-system@v1
with:
  MODULE: 'alpine-base'
  VERSION_FILE: "docker/alpine-base/version.txt"

# Using underscore
uses: sanjeevkumarraob/version-system@v1
with:
  MODULE: 'my_cli'
  VERSION_FILE: "modules/my_cli/version.txt"
```

### A simple semver without any prefix, suffix etc

```yaml
uses: sanjeevkumarraob/version-system@v1
with:
  VERSION_FILE: "version.txt"
```

### A simple semver with automated release

```yaml
uses: sanjeevkumarraob/version-system@v1
with:
  VERSION_FILE: "version.txt"
  CREATE_RELEASE: true
```

## Local Development

### Running Tests

```bash
# Run all tests
make run_test

# Or use the test runner script
./run_tests.sh all

# Run specific test types
./run_tests.sh unit
./run_tests.sh integration
./run_tests.sh coverage
```

### Manual Testing

```bash
# Basic version generation
GITHUB_OUTPUT=/tmp/output python3 get_version.py -f version.txt -r .

# With prefix
GITHUB_OUTPUT=/tmp/output python3 get_version.py -f version.txt -r . -p dev

# With module
GITHUB_OUTPUT=/tmp/output python3 get_version.py -f version.txt -r . -m my-module
```

## Release Process

This project uses our own version-system action for releases - perfect dogfooding!

### For Maintainers

1. **Create a new release**: Use the "Version Bump and Tag" workflow in GitHub Actions
   - Go to Actions → Version Bump and Tag → Run workflow
   - Choose version type (patch/minor/major) or specify custom version
   - Our action automatically handles everything:
     - ✅ Version calculation based on existing tags
     - ✅ Tag creation
     - ✅ Release creation with auto-generated notes
     - ✅ Major version tag updates (v1, v2, etc.)

2. **version.txt**: Stays stable at `1.0.0` as reference
   - Never needs manual updates
   - Used by our action as base reference only

### Version Strategy

- **v1.x.x**: Current stable version
- **v2.x.x**: Future major version (breaking changes)
- **Major tags** (v1, v2): Always point to latest patch of that major version

### CI/CD Workflows

- **CI**: Runs tests on all pull requests and pushes
- **Version Bump**: Complete automated release process using our own action

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

If you encounter any issues or have questions, please [open an issue](https://github.com/sanjeevkumarraob/version-system/issues) on GitHub.
