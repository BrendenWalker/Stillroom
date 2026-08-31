from decimal import Decimal
from types import SimpleNamespace

from cookbook.helper.food_pack import (
    apply_food_pack_fields,
    derive_shopping_measure_grams,
    in_store_shopping_count,
    quantity_to_grams,
    shopping_entry_quantities,
    shopping_units_to_grams,
)


def test_derive_shopping_measure_grams():
    assert derive_shopping_measure_grams(50, 12, 999) == Decimal('600.00')
    assert derive_shopping_measure_grams(50, 1) == Decimal('50.00')
    assert derive_shopping_measure_grams(None, 12, 425) == Decimal('425')
    assert derive_shopping_measure_grams(None, None, None) is None


def test_apply_food_pack_fields_derives_and_fills_count_one():
    iug, derived, error = apply_food_pack_fields(50, 12, 1)
    assert error is None
    assert iug == Decimal('50')
    assert derived == Decimal('600.00')

    iug, derived, error = apply_food_pack_fields(None, 1, 50)
    assert error is None
    assert iug == Decimal('50')
    assert derived == Decimal('50.00')

    iug, derived, error = apply_food_pack_fields(80, 1, None)
    assert error is None
    assert iug == Decimal('80')
    assert derived == Decimal('80.00')


def test_apply_food_pack_fields_rejects_invalid_count():
    _, _, error = apply_food_pack_fields(50, 0, 50)
    assert error is not None
    _, _, error = apply_food_pack_fields(50, -1, 50)
    assert error is not None


def test_quantity_to_grams_weight_and_each():
    food = SimpleNamespace(ingredient_unit_grams=Decimal('50'), shopping_measure='dozen', shopping_measure_grams=Decimal('600'), space=None)
    gram = SimpleNamespace(name='g', base_unit='g')
    each = SimpleNamespace(name='each', base_unit='')
    dozen = SimpleNamespace(name='dozen', base_unit='')

    assert quantity_to_grams(food, 100, gram) == Decimal('100')
    assert quantity_to_grams(food, 3, each) == Decimal('150')
    assert quantity_to_grams(food, 3, None) == Decimal('150')
    assert quantity_to_grams(food, 1, dozen) == Decimal('600')


def test_quantity_to_grams_count_unit_aliases():
    food = SimpleNamespace(ingredient_unit_grams=Decimal('50'), shopping_measure='dozen', shopping_measure_grams=Decimal('600'), space=None)
    eggs = SimpleNamespace(name='eggs', base_unit='')
    stk = SimpleNamespace(name='Stk.', base_unit='')
    cup = SimpleNamespace(name='cup', base_unit='')

    assert quantity_to_grams(food, 3, eggs) == Decimal('150')
    assert quantity_to_grams(food, 3, stk) == Decimal('150')
    assert quantity_to_grams(food, 2, cup) is None


def test_shopping_entry_quantities_pack_and_legacy():
    packed = SimpleNamespace(ingredient_unit_grams=Decimal('50'), shopping_measure='dozen', shopping_measure_grams=Decimal('600'), space=None)
    each = SimpleNamespace(name='each', base_unit='')
    amount, unit, grams = shopping_entry_quantities(packed, 3, each)
    assert grams == Decimal('150')
    assert unit is None
    assert amount == Decimal('150') / Decimal('600')

    unpacked = SimpleNamespace(ingredient_unit_grams=None, shopping_measure=None, shopping_measure_grams=None, space=None)
    cup = SimpleNamespace(name='cup', base_unit='')
    amount, unit, grams = shopping_entry_quantities(unpacked, 2, cup)
    assert grams is None
    assert amount == Decimal('2')
    assert unit is cup


def test_parsed_amount_uses_ingredient_unit_not_shopping_packs():
    """Telegram / free-text '3 eggs' must convert as 3 each, not 3 dozen."""
    packed = SimpleNamespace(ingredient_unit_grams=Decimal('50'), shopping_measure='dozen', shopping_measure_grams=Decimal('600'), space=None)
    each = SimpleNamespace(name='each', base_unit='')
    amount, unit, grams = shopping_entry_quantities(packed, 3, each)
    assert grams == Decimal('150')
    assert amount == Decimal('150') / Decimal('600')


def test_in_store_shopping_count_ceils():
    assert in_store_shopping_count(150, 600) == 1
    assert in_store_shopping_count(600, 600) == 1
    assert in_store_shopping_count(601, 600) == 2


def test_shopping_units_to_grams():
    food = SimpleNamespace(shopping_measure_grams=Decimal('600'))
    assert shopping_units_to_grams(food, 1) == Decimal('600')
    assert shopping_units_to_grams(food, 2) == Decimal('1200')
