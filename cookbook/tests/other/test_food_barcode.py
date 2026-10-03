from cookbook.helper.food_barcode import canonicalize_upc


UPC_A = '012345678905'
EAN_13 = '0012345678905'
EAN_8 = '96385074'
INVALID_CHECK = '012345678901'


def test_canonicalize_upc_a_to_ean13():
    canonical, error = canonicalize_upc(UPC_A)
    assert error is None
    assert canonical == EAN_13


def test_canonicalize_ean13_and_gtin14():
    canonical, error = canonicalize_upc(EAN_13)
    assert error is None
    assert canonical == EAN_13

    canonical, error = canonicalize_upc('0' + EAN_13)
    assert error is None
    assert canonical == EAN_13


def test_canonicalize_ean8():
    canonical, error = canonicalize_upc(EAN_8)
    assert error is None
    assert canonical == EAN_8


def test_canonicalize_strips_non_digits():
    canonical, error = canonicalize_upc('0 12345 67890 5')
    assert error is None
    assert canonical == EAN_13


def test_canonicalize_rejects_checksum_and_length():
    canonical, error = canonicalize_upc(INVALID_CHECK)
    assert canonical is None
    assert error is not None

    canonical, error = canonicalize_upc('12345')
    assert canonical is None
    assert error is not None

    canonical, error = canonicalize_upc('')
    assert canonical is None
    assert error is not None
