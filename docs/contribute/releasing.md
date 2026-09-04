# Releasing

Public notes live in [`CHANGELOG.md`](https://github.com/BrendenWalker/Stillroom/blob/develop/CHANGELOG.md). GitHub Releases are published automatically when a version tag is pushed. The tag commit **must** already contain a matching changelog heading, or the release workflow fails and no GitHub Release is created.

Version tags are `X.Y.Z` with no `v` prefix (for example `1.2.3`). That matches GHCR image tags. A hyphen in the tag (`1.2.3-beta.1`) marks a prerelease and is not set as latest.

## Pull requests

Every pull request updates the `[Unreleased]` section in `CHANGELOG.md`, or is labeled `skip-changelog`. Use `breaking-change` when the change includes a breaking API, settings, or database migration. Put upgrade warnings in a short paragraph above the Keep a Changelog categories.

## Cut a release

1. On `develop`, move `[Unreleased]` into a versioned section. Leave an empty `[Unreleased]` heading for the next cycle. Update the compare links at the bottom of the file.

```markdown
## [Unreleased]

## [1.2.3] - 2026-09-04

Upgrade notes go here if operators must take a backup or handle a migration.

### Added

- ...
```

2. Confirm the section extracts (this is the same check the workflow runs):

```bash
python scripts/extract_changelog.py 1.2.3
```

3. Commit the changelog, then tag **that** commit and push the tag. Do not tag first.

```bash
git add CHANGELOG.md
git commit -m "Release 1.2.3"
git tag 1.2.3
git push origin develop
git push origin 1.2.3
```

Pushing the tag starts two workflows: Docker publishes `ghcr.io/brendenwalker/stillroom` (`1.2.3`, `1.2`, `1`, and `latest` for a stable tag). The release workflow publishes [GitHub Releases](https://github.com/BrendenWalker/Stillroom/releases) with the changelog section first and the auto-generated pull request list after it.

If the generated pull request list needs a pass, edit the GitHub Release. Do not fix notes by tagging a commit that never had the `## [X.Y.Z]` heading.

<!-- prettier-ignore-start -->
!!! danger "Tagging without a changelog section fails"
     `scripts/extract_changelog.py` looks for `## [X.Y.Z]` in `CHANGELOG.md` on the tagged commit. A missing or empty section fails the job. The git tag can still exist. Add the section, commit, and move the tag to the new commit only if GHCR has not already published that tag; otherwise bump to the next patch version.
<!-- prettier-ignore-end -->
