import importlib
from decimal import Decimal

from django.apps import apps
from django_scopes import scopes_disabled

from cookbook.models import Food, Property, PropertyType, Unit

migration = importlib.import_module(
    'cookbook.migrations.0248_backfill_food_kcal_shopping_measure_grams'
)
backfill_food_kcal_and_shopping_grams = migration.backfill_food_kcal_and_shopping_grams


def test_backfill_copies_calories_pair_when_both_null(space_1):
    with scopes_disabled():
        unit = Unit.objects.create(name='gram', base_unit='g', space=space_1)
        calories = PropertyType.objects.create(name='Calories', unit='kcal', fdc_id=1008, space=space_1)
        food = Food.objects.create(
            name='null kcal food',
            space=space_1,
            properties_food_amount=100,
            properties_food_unit=unit,
        )
        prop = Property.objects.create(property_type=calories, property_amount=Decimal('274'), space=space_1)
        food.properties.add(prop)

        backfill_food_kcal_and_shopping_grams(apps, None)
        food.refresh_from_db()
        assert food.kcal == Decimal('274')
        assert food.kcal_grams == Decimal('100')


def test_backfill_does_not_overwrite_existing_kcal(space_1):
    with scopes_disabled():
        unit = Unit.objects.create(name='gram', base_unit='g', space=space_1)
        calories = PropertyType.objects.create(name='Calories', unit='kcal', space=space_1)
        food = Food.objects.create(
            name='existing kcal food',
            space=space_1,
            kcal=Decimal('10'),
            kcal_grams=Decimal('50'),
            properties_food_amount=100,
            properties_food_unit=unit,
        )
        prop = Property.objects.create(property_type=calories, property_amount=Decimal('274'), space=space_1)
        food.properties.add(prop)

        backfill_food_kcal_and_shopping_grams(apps, None)
        food.refresh_from_db()
        assert food.kcal == Decimal('10')
        assert food.kcal_grams == Decimal('50')


def test_backfill_skips_when_only_one_kcal_field_set(space_1):
    with scopes_disabled():
        unit = Unit.objects.create(name='gram', base_unit='g', space=space_1)
        calories = PropertyType.objects.create(name='Calories', unit='kcal', space=space_1)
        food = Food.objects.create(
            name='partial kcal food',
            space=space_1,
            kcal=Decimal('10'),
            properties_food_amount=100,
            properties_food_unit=unit,
        )
        prop = Property.objects.create(property_type=calories, property_amount=Decimal('274'), space=space_1)
        food.properties.add(prop)

        backfill_food_kcal_and_shopping_grams(apps, None)
        food.refresh_from_db()
        assert food.kcal == Decimal('10')
        assert food.kcal_grams is None


def test_backfill_shopping_measure_grams_when_null(space_1):
    with scopes_disabled():
        shopping_type = PropertyType.objects.create(
            name='Grams in shopping measure',
            unit='g',
            space=space_1,
        )
        food = Food.objects.create(name='pack food', space=space_1)
        already = Food.objects.create(
            name='already packed',
            space=space_1,
            shopping_measure_grams=Decimal('400'),
        )
        untouched = Food.objects.create(name='no props', space=space_1)
        prop = Property.objects.create(
            property_type=shopping_type,
            property_amount=Decimal('600'),
            space=space_1,
        )
        already_prop = Property.objects.create(
            property_type=shopping_type,
            property_amount=Decimal('999'),
            space=space_1,
        )
        food.properties.add(prop)
        already.properties.add(already_prop)

        backfill_food_kcal_and_shopping_grams(apps, None)
        food.refresh_from_db()
        already.refresh_from_db()
        untouched.refresh_from_db()
        assert food.shopping_measure_grams == Decimal('600')
        assert already.shopping_measure_grams == Decimal('400')
        assert untouched.shopping_measure_grams is None
