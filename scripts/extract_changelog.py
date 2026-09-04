#!/usr/bin/env python3
"""Extract a version section from CHANGELOG.md for GitHub Releases."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CHANGELOG_PATH = REPO_ROOT / 'CHANGELOG.md'
HEADING_RE = re.compile(r'^## \[([^\]]+)\](.*)$')
LINK_DEF_RE = re.compile(r'^\[[^\]]+\]:\s+\S+')


def extract_section(text: str, version: str) -> str:
    """Return the Keep a Changelog section for ``version``.

    Raises ValueError if the heading is missing or the section is empty.
    """
    lines = text.splitlines()
    start = None
    for index, line in enumerate(lines):
        match = HEADING_RE.match(line)
        if match and match.group(1) == version:
            start = index
            break
    if start is None:
        raise ValueError(f'No CHANGELOG.md section for version {version}')

    end = len(lines)
    for index in range(start + 1, len(lines)):
        if HEADING_RE.match(lines[index]):
            end = index
            break

    body_lines = []
    for line in lines[start:end]:
        if LINK_DEF_RE.match(line):
            continue
        body_lines.append(line)

    section = '\n'.join(body_lines).strip()
    if not section:
        raise ValueError(f'CHANGELOG.md section for version {version} is empty')
    return section + '\n'


def _self_test() -> int:
    sample = '\n'.join([
        '# Changelog',
        '',
        '## [Unreleased]',
        '',
        '### Added',
        '',
        '- pending',
        '',
        '## [1.2.3] - 2026-09-04',
        '',
        '### Fixed',
        '',
        '- crash on empty shopping list',
        '',
        '[Unreleased]: https://example.com/unreleased',
        '[1.2.3]: https://example.com/1.2.3',
        '',
    ])
    extracted = extract_section(sample, '1.2.3')
    assert '## [1.2.3] - 2026-09-04' in extracted
    assert '- crash on empty shopping list' in extracted
    assert 'pending' not in extracted
    assert 'https://example.com' not in extracted
    try:
        extract_section(sample, '9.9.9')
    except ValueError:
        pass
    else:
        raise AssertionError('expected missing version to raise ValueError')
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('version', nargs='?', help='Version heading to extract, for example 1.2.3')
    parser.add_argument('--changelog', type=Path, default=CHANGELOG_PATH, help='Path to CHANGELOG.md')
    parser.add_argument('--self-test', action='store_true', help='Run built-in parser checks and exit')
    args = parser.parse_args(argv)

    if args.self_test:
        return _self_test()
    if not args.version:
        parser.error('version is required unless --self-test is set')

    try:
        text = args.changelog.read_text(encoding='utf-8')
        sys.stdout.write(extract_section(text, args.version))
    except (OSError, ValueError) as exc:
        print(exc, file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
