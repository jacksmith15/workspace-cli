# Home

**Workspace** streamlines management and adoption of mono-repositories, by providing a lightweight wrapper around multi-repo tooling.

It was initially implemented to manage Python projects, but can be extended to interpret other types of projects.


## Core concepts

- A **workspace** is a collection of projects, under a single root directory (usually the root directory of a git repository)
- Each **project** is equivalent to a single repository in a multi-repo strategy. It specifies its own tooling for testing, building, etc.

## Key features

The CLI tool stores lightweight metadata in the repository and provides:

- Inter-project dependency inference
- Environment-aware command runner with support for parallelisation over projects
- Compatibility with multi-repo tooling
- Define and use custom templates for new projects
- Plugin support for custom project types

## Motivation

There are many advantages to a mono-repo strategy. Some commonly mentioned ones are:

- **Atomic changes**: A system change which affects multiple components is still only a single change in source control, which reducing the number of barriers to delivery.
- **Code reuse**: Its easy to share code between different projects, as there is no need to set-up a new repository to contain the shared code.
- **Ease of refactoring**: When each project is a separate repository, its harder to redraw the boundaries of those projects. Because of this, its tempting to add new functionality in places where it doesn't belong.
- **Cognitive overhead**: If a multi-repo system grows to include a large number of components, it can be daunting for new contributors to identify and understand the wider picture, and the relationships between projects.

These benefits come with some new challenges, for example:

- Boundaries between projects (previously implicit in the repository boundary) can become less well-defined.
- Smarter automation/continuous integration is required, or else changes to a single project can result in a time-consuming build cycle for all projects.

**Workspace** tries to alleviate these challenges _without_ impacting per-project tooling choices. Its underlying philosophy is that each project should be **extricable** from the wider project, so that:

- Project boundaries are as clear as they would be in a multi-repo strategy.
- Maintainers of a particular project can use the build and development tools they are familiar with.
- It is trivial to migrate projects in (and out) of the mono-repo.
