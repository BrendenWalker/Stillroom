from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from math import ceil

from cookbook.helper.unit_conversion_helper import BASE_UNITS_WEIGHT, ConversionException, UnitConversionHelper

COUNT_UNIT_NAMES = {'each', 'ea', 'piece', 'pcs', 'pc', 'item'}
GRAM_UNIT_NAMES = {'g', 'gram', 'grams'}
CEIL_EPS = 1e-9


def to_decimal(value):
    if value is None or value == '':
        return None
    try:
        d = Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        return None
    if not d.is_finite():
        return None
    return d


def derive_shopping_measure_grams(ingredient_unit_grams, count_per_pack, shopping_measure_grams=None):
    iug = to_decimal(ingredient_unit_grams)
    cpp = to_decimal(count_per_pack)
    if iug is not None and cpp is not None and iug > 0 and cpp > 0:
        return (iug * cpp).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    return to_decimal(shopping_measure_grams)


def validate_count_per_pack_one(ingredient_unit_grams, count_per_pack, shopping_measure_grams):
    cpp = to_decimal(count_per_pack)
    if cpp is None or int(cpp) != 1:
        return None
    iug = to_decimal(ingredient_unit_grams)
    smg = to_decimal(shopping_measure_grams)
    has_i = iug is not None
    has_s = smg is not None
    if not has_i and not has_s:
        return None
    if not has_i or not has_s:
        return 'When count per pack is 1, set ingredient unit (grams) and grams in shopping measure to the same value.'
    if abs(iug - smg) > Decimal('1e-9'):
        return 'When count per pack is 1, ingredient unit (grams) and grams in shopping measure must match.'
    return None


def apply_food_pack_fields(ingredient_unit_grams, count_per_pack, shopping_measure_grams=None):
    """
    Derive shopping_measure_grams then validate count_per_pack == 1.
    Returns (shopping_measure_grams, error_message).
    """
    derived = derive_shopping_measure_grams(ingredient_unit_grams, count_per_pack, shopping_measure_grams)
    error = validate_count_per_pack_one(ingredient_unit_grams, count_per_pack, derived)
    return derived, error


def shopping_measure_grams_of(food):
    if food is None:
        return None
    return to_decimal(getattr(food, 'shopping_measure_grams', None))


def shopping_units_to_grams(food, units):
    smg = shopping_measure_grams_of(food)
    units = to_decimal(units)
    if smg is None or smg <= 0 or units is None:
        return None
    return units * smg


def grams_to_shopping_units(grams, food):
    g = to_decimal(grams)
    if g is None:
        return None
    smg = shopping_measure_grams_of(food)
    if smg is None or smg <= 0:
        return g
    return g / smg


def in_store_shopping_count(grams, shopping_measure_grams):
    g = to_decimal(grams)
    if g is None:
        return None
    smg = to_decimal(shopping_measure_grams)
    if smg is None or smg <= 0:
        return int(ceil(float(g) - CEIL_EPS))
    units = float(g / smg)
    return int(ceil(units - CEIL_EPS))


def _unit_name(unit):
    if unit is None:
        return ''
    return str(getattr(unit, 'name', '') or '').strip().lower()


def _is_count_unit(unit):
    if unit is None:
        return True
    name = _unit_name(unit)
    if name in COUNT_UNIT_NAMES:
        return True
    base = getattr(unit, 'base_unit', None)
    return not base and name in COUNT_UNIT_NAMES


def _is_gram_unit(unit):
    if unit is None:
        return False
    base = getattr(unit, 'base_unit', None)
    if base == 'g':
        return True
    return _unit_name(unit) in GRAM_UNIT_NAMES


def quantity_to_grams(food, amount, unit, space=None):
    """
    Convert an amount+unit for a food into grams, or None if it cannot be converted.
    """
    amount = to_decimal(amount)
    if amount is None or food is None:
        return None

    base = getattr(unit, 'base_unit', None) if unit is not None else None
    if base in BASE_UNITS_WEIGHT:
        try:
            return UnitConversionHelper.convert_from_to(base, 'g', amount)
        except ConversionException:
            pass

    iug = to_decimal(getattr(food, 'ingredient_unit_grams', None))
    if _is_count_unit(unit) and iug is not None and iug > 0:
        return amount * iug

    smg = shopping_measure_grams_of(food)
    shopping_measure = str(getattr(food, 'shopping_measure', None) or '').strip().lower()
    if unit is not None and shopping_measure and _unit_name(unit) == shopping_measure and smg is not None and smg > 0:
        return amount * smg

    space = space or getattr(food, 'space', None)
    if unit is not None and space is not None:
        from cookbook.models import Ingredient
        helper = UnitConversionHelper(space)
        probe = Ingredient(amount=amount, unit=unit, food=food, space=space)
        try:
            conversions = helper.get_conversions(probe)
        except Exception:
            conversions = []
        for converted in conversions:
            if _is_gram_unit(getattr(converted, 'unit', None)):
                grams = to_decimal(converted.amount)
                if grams is not None:
                    return grams

    return None


def ingredient_to_grams(ingredient, food=None):
    if ingredient is None:
        return None
    food = food or getattr(ingredient, 'food', None)
    return quantity_to_grams(food, getattr(ingredient, 'amount', None), getattr(ingredient, 'unit', None), space=getattr(ingredient, 'space', None))


def shopping_entry_quantities(food, amount, unit=None, amount_grams=None):
    """
    Return (amount, unit, amount_grams) to persist on ShoppingListEntry.

    amount_grams is canonical when pack conversion succeeds. When the food has
    shopping_measure_grams, amount is stored as shopping-unit count and unit is cleared.
    """
    amount = to_decimal(amount)
    if amount is None:
        amount = Decimal(0)

    grams = to_decimal(amount_grams)
    if grams is None:
        grams = quantity_to_grams(food, amount, unit)

    smg = shopping_measure_grams_of(food)
    if grams is not None and smg is not None and smg > 0:
        return grams / smg, None, grams

    return amount, unit, grams
