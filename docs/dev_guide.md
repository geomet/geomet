# Development Guide

## Packaging and Releasing New Versions to PyPI

Follow these steps for release new versions of `geomet` to https://pypi.org/.

NOTE: Only members of the `Owners` team on GitHub have the permissions to
trigger a release of a new package versions to PyPI.

NOTE: Release branches should not include new features or bug fixes, unless
prescribed by the process below.

1. Update the major or minor version string in `geomet/__init__.py`, following
  https://semver.org/ guidelines.
2. Create a new branch called `release-X.Y`, where X is the major version,
  Y is the minor version.
3. Push the branch to the central repo: https://github.com/geomet/geomet.
4. Open a pull request from branch `release-X.Y` to the `master` branch.
5. Ensure that all CI/CD tests and checks pass.
6. Obtain a review/approval from a Maintainer.
7. Trigger the manual approval gate in CircleCI to publish the package.
8. Verify that the publishing step was successul. (Check CircleCI output, check PyPI.)
9. Merge the pull request.
10. Create a Tag and a Release from the head commit of the branch. The release
   text should contain some relevant information about features/bugfixes that
   have been added since the last release.
11. Delete the `release-X.Y.Z` branch.

NOTE: Sometimes releases don't always work on the first try. If something goes
wrong while publishing to PyPI, due to tooling errors, bugs, misconfigurations,
etc.:

1. Add 1 or more new commits to attempt to fix the issue and push to the `release-X.Y` branch
2. Increment the "patch" version (the last number) in the
version string in `geomet/__init__.py`. As a separate commit from the fix.
3. Repeat the process above beginning from step 5.
