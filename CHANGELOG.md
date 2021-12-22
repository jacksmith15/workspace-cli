# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog] and this project adheres to
[Semantic Versioning].

Types of changes are:
* **Security** in case of vulnerabilities.
* **Deprecated** for soon-to-be removed features.
* **Added** for new features.
* **Changed** for changes in existing functionality.
* **Removed** for now removed features.
* **Fixed** for any bug fixes.

## [Unreleased]
### Fixed
* Removed extra period in an error message.


## [0.3.0] - 2021-12-02
### Added
* Some automatic template variables can now be included: `workspace_project_path` and `workspace_project_name`.

### Changed
* `sync` now uses the same no-op logic as `run` and `list` (see [[0.2.0]] below).

## [0.2.0] - 2021-11-23
### Changed
* `run` and `list` are now no-ops when input is piped to the command, and no arguments are provided. Behaviour when providing regular arguments is unchanged. This makes these commands easier to chain in scripts. E.g.
  - `workspace reverse | workspace run` will not run any commands
  - `workspace run` will still run a command in every project

## [0.1.0] - 2021-11-01
### Added
* Project started :)
* Added initial feature-set:
  - Create and add projects to a workspace
  - Inspect inter-dependencies between projects
  - Run commands over multiple projects (serial or parallel)
  - Use custom templates
  - Add plugins containing custom project type adapters

[Unreleased]: https://github.com/jacksmith15/workspace-cli/compare/0.3.0..HEAD
[0.3.0]: https://github.com/jacksmith15/workspace-cli/compare/0.2.0..0.3.0
[0.2.0]: https://github.com/jacksmith15/workspace-cli/compare/0.1.0..0.2.0
[0.1.0]: https://github.com/jacksmith15/workspace-cli/compare/initial..0.1.0

[Keep a Changelog]: http://keepachangelog.com/en/1.0.0/
[Semantic Versioning]: http://semver.org/spec/v2.0.0.html

[_release_link_format]: https://github.com/jacksmith15/workspace-cli/compare/{previous_tag}..{tag}
[_breaking_change_token]: BREAKING
