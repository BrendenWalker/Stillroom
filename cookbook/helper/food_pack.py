from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from math import ceil

from django.utils.translation import gettext as _

from cookbook.helper.unit_conversion_helper import BASE_UNITS_WEIGHT, ConversionException, UnitConversionHelper

# Names treated as a countable "each" when converting recipe amounts to grams.
# Keep this to piece/count words (not cups, grams, or other measures).
# Add locale aliases here; migration 0246 has a frozen copy and must not import this set.
COUNT_UNIT_NAMES = {
    'each', 'ea', 'piece', 'pieces', 'pcs', 'pc', 'pce', 'item', 'items',
    'egg', 'eggs',
    'unit', 'units',
    'count', 'whole',
    'stk', 'stück', 'stuck', 'stueck', 'stücke', 'stuecke',
    'stuk', 'stuks',
    'pieza', 'piezas',
    'pezzo', 'pezzi', 'pz',
    'unidade', 'unidades',
    'szt',
    'ks', 'kus',
    'шт', 'штука',
    '个',
}
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


def apply_food_pack_fields(ingredient_unit_grams, count_per_pack, shopping_measure_grams=None):
    """
    Normalize pack fields: reject invalid counts, fill the missing gram field when
    count_per_pack is 1, then derive shopping_measure_grams from unit grams × count.
    Returns (ingredient_unit_grams, shopping_measure_grams, error_message).
    """
    cpp = to_decimal(count_per_pack)
    iug = to_decimal(ingredient_unit_grams)
    smg = to_decimal(shopping_measure_grams)

    if cpp is not None:
        if cpp < 1:
            return iug, smg, _('Count per pack must be at least 1.')
        if cpp != cpp.to_integral_value():
            return iug, smg, _('Count per pack must be a whole number.')

    if cpp is not None and cpp == 1:
        if iug is None and smg is not None and smg > 0:
            iug = smg
        elif smg is None and iug is not None and iug > 0:
            smg = iug

    derived = derive_shopping_measure_grams(iug, cpp, smg)
    return iug, derived, None


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
    return str(getattr(unit, 'name', '') or '').strip().lower().rstrip('.')


def _is_count_unit(unit):
    if unit is None:
        return True
    return _unit_name(unit) in COUNT_UNIT_NAMES


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
