from types import SimpleNamespace

from cookbook.helper.food_availability_helper import is_food_item


def test_is_food_item_none():
    assert is_food_item(None) is False


def test_is_food_item_uncategorized():
    assert is_food_item(SimpleNamespace(supermarket_category=None)) is True


def test_is_food_item_food_category():
    assert is_food_item(SimpleNamespace(supermarket_category=SimpleNamespace(is_food=True))) is True


def test_is_food_item_non_food_category():
    assert is_food_item(SimpleNamespace(supermarket_category=SimpleNamespace(is_food=False))) is False
