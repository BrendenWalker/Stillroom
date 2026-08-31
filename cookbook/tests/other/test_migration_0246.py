import importlib
from decimal import Decimal
from types import SimpleNamespace

from django.apps import apps
from django.contrib import auth
from django_scopes import scopes_disabled

from cookbook.models import Food, ShoppingListEntry
from cookbook.tests.factories import FoodFactory, ShoppingListEntryFactory, UnitFactory

migration = importlib.import_module(
    'cookbook.migrations.0246_food_count_per_pack_min_backfill_amount_grams'
)
shopping_entry_quantities = migration.shopping_entry_quantities
backfill_shopping_amount_grams = migration.backfill_shopping_amount_grams


def test_migration_quantities_count_unit_to_shopping_packs():
    packed = SimpleNamespace(
        ingredient_unit_grams=Decimal('50'),
        shopping_measure='dozen',
        shopping_measure_grams=Decimal('600'),
    )
    each = SimpleNamespace(name='each', base_unit='')
    amount, unit, grams = shopping_entry_quantities(packed, 3, each)
    assert grams == Decimal('150')
    assert unit is None
    assert amount == Decimal('150') / Decimal('600')


def test_migration_quantities_weight_base_unit():
    packed = SimpleNamespace(
        ingredient_unit_grams=Decimal('50'),
        shopping_measure='can',
        shopping_measure_grams=Decimal('400'),
    )
    gram = SimpleNamespace(name='g', base_unit='g')
    amount, unit, grams = shopping_entry_quantities(packed, 200, gram)
    assert grams == Decimal('200')
    assert unit is None
    assert amount == Decimal('200') / Decimal('400')


def test_backfill_sets_amount_grams_and_clears_unit(u1_s1, space_1):
    user = auth.get_user(u1_s1)
    with scopes_disabled():
        food = FoodFactory(
            space=space_1,
            shopping_measure='dozen',
            ingredient_unit_grams=Decimal('50'),
            count_per_pack=12,
            shopping_measure_grams=Decimal('600'),
        )
        each = UnitFactory(space=space_1, name='each')
        sle = ShoppingListEntryFactory(
            space=space_1,
            food=food,
            unit=each,
            amount=Decimal('3'),
            amount_grams=None,
            created_by=user,
        )
        invalid = FoodFactory(space=space_1)
        Food.objects.filter(pk=invalid.pk).update(count_per_pack=0)

        backfill_shopping_amount_grams(apps, None)

        sle = ShoppingListEntry.objects.get(pk=sle.pk)
        assert sle.amount_grams == Decimal('150')
        assert sle.unit_id is None
        assert sle.amount == Decimal('150') / Decimal('600')

        invalid.refresh_from_db()
        assert invalid.count_per_pack is None
