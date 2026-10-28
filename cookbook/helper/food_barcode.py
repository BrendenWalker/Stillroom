"""Normalize and validate grocery barcodes (UPC-A, UPC-E, EAN-8/13, GTIN-14)."""

from __future__ import annotations

import re

from django.utils.translation import gettext as _

_NON_DIGITS = re.compile(r'\D+')

INVALID_CHECKSUM = 'Invalid barcode checksum.'
INVALID_LENGTH = 'Barcode must be UPC-A, EAN-8, EAN-13, or GTIN-14.'
EMPTY = 'Enter a barcode.'


def _checksum_ok(digits: str) -> bool:
    if len(digits) < 8:
        return False
    body, check = digits[:-1], int(digits[-1])
    total = 0
    for index, char in enumerate(reversed(body)):
        total += int(char) * (3 if index % 2 == 0 else 1)
    return (10 - (total % 10)) % 10 == check


def _expand_upc_e(digits: str) -> str | None:
    """Expand 8-digit UPC-E (number system + 6 data + check) to UPC-A."""
    if len(digits) != 8:
        return None
    number_system, data, check = digits[0], digits[1:7], digits[7]
    last = data[5]
    if last in '012':
        upc_a = f'{number_system}{data[0:2]}{last}0000{data[2:5]}{check}'
    elif last == '3':
        upc_a = f'{number_system}{data[0:3]}00000{data[3:5]}{check}'
    elif last == '4':
        upc_a = f'{number_system}{data[0:4]}00000{data[4]}{check}'
    else:
        upc_a = f'{number_system}{data[0:5]}0000{last}{check}'
    if _checksum_ok(upc_a):
        return upc_a
    return None


def canonicalize_upc(raw: str | None) -> tuple[str | None, str | None]:
    """Return ``(canonical_digits, error_message)``.

    Canonical form:
    - EAN-8 stays 8 digits
    - UPC-A (12) is stored as EAN-13 with a leading 0
    - EAN-13 stays 13
    - GTIN-14 with a leading 0 is stored as EAN-13; otherwise 14
    - UPC-E (8 digits that fail EAN-8 checksum) is expanded to UPC-A then EAN-13
    """
    if raw is None:
        return None, _(EMPTY)
    digits = _NON_DIGITS.sub('', str(raw))
    if not digits:
        return None, _(EMPTY)

    if len(digits) == 12:
        if not _checksum_ok(digits):
            return None, _(INVALID_CHECKSUM)
        return '0' + digits, None

    if len(digits) == 13:
        if not _checksum_ok(digits):
            return None, _(INVALID_CHECKSUM)
        return digits, None

    if len(digits) == 14:
        if not _checksum_ok(digits):
            return None, _(INVALID_CHECKSUM)
        if digits.startswith('0'):
            return digits[1:], None
        return digits, None

    if len(digits) == 8:
        if _checksum_ok(digits):
            return digits, None
        upc_a = _expand_upc_e(digits)
        if upc_a:
            return '0' + upc_a, None
        return None, _(INVALID_CHECKSUM)

    return None, _(INVALID_LENGTH)
