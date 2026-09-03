import json
from decimal import Decimal

from django.contrib import auth
from django.test import RequestFactory
from django_scopes import scope
from rest_framework.renderers import JSONRenderer

from cookbook.models import Food, Ingredient
from cookbook.serializer import RecipeExportSerializer
from cookbook.tests.factories import FoodFactory, RecipeFactory, StepFactory, UnitFactory


def _request(client):
    user = auth.get_user(client)
    user_space = user.userspace_set.first()
    request = RequestFactory().get('/')
    request.user = user
    request.space = user_space.space
    request.user_space = user_space
    return request


def _round_trip_payload(recipe):
    data = RecipeExportSerializer(recipe).data
    return json.loads(JSONRenderer().render(data))


def test_recipe_export_includes_food_detail_fields(space_1, u1_s1):
    with scope(space=space_1):
        food = FoodFactory(
            space=space_1,
            name='Egg',
            shopping_measure='Dozen',
            ingredient_unit_grams=Decimal('50.00'),
            count_per_pack=12,
            shopping_measure_grams=Decimal('600.00'),
            kcal=Decimal('72.00'),
            kcal_grams=Decimal('50.00'),
        )
        unit = UnitFactory(space=space_1, name='each')
        step = StepFactory(space=space_1, ingredients__count=0)
        ingredient = Ingredient.objects.create(
            food=food, unit=unit, amount=3, space=space_1,
        )
        step.ingredients.add(ingredient)
        recipe = RecipeFactory(
            space=space_1,
            created_by=auth.get_user(u1_s1),
            internal=True,
            steps__count=0,
            keywords__count=0,
        )
        recipe.steps.add(step)
        payload = _round_trip_payload(recipe)

    exported_food = payload['steps'][0]['ingredients'][0]['food']
    assert exported_food['name'] == 'Egg'
    assert exported_food['shopping_measure'] == 'Dozen'
    assert float(exported_food['ingredient_unit_grams']) == 50
    assert exported_food['count_per_pack'] == 12
    assert float(exported_food['shopping_measure_grams']) == 600
    assert float(exported_food['kcal']) == 72
    assert float(exported_food['kcal_grams']) == 50


def test_recipe_import_creates_food_detail_fields(space_1, space_2, u1_s1, u1_s2):
    with scope(space=space_1):
        food = FoodFactory(
            space=space_1,
            name='Egg',
            shopping_measure='Dozen',
            ingredient_unit_grams=Decimal('50.00'),
            count_per_pack=12,
            shopping_measure_grams=Decimal('600.00'),
            kcal=Decimal('72.00'),
            kcal_grams=Decimal('50.00'),
        )
        unit = UnitFactory(space=space_1, name='each')
        step = StepFactory(space=space_1, ingredients__count=0)
        step.ingredients.add(Ingredient.objects.create(
            food=food, unit=unit, amount=3, space=space_1,
        ))
        recipe = RecipeFactory(
            space=space_1,
            created_by=auth.get_user(u1_s1),
            internal=True,
            steps__count=0,
            keywords__count=0,
        )
        recipe.steps.add(step)
        payload = _round_trip_payload(recipe)

    request = _request(u1_s2)
    serializer = RecipeExportSerializer(data=payload, context={'request': request})
    assert serializer.is_valid(), serializer.errors
    with scope(space=space_2):
        imported = serializer.save()
        imported_food = imported.steps.first().ingredients.first().food
        assert imported_food.name == 'Egg'
        assert imported_food.shopping_measure == 'Dozen'
        assert imported_food.ingredient_unit_grams == Decimal('50.00')
        assert imported_food.count_per_pack == 12
        assert imported_food.shopping_measure_grams == Decimal('600.00')
        assert imported_food.kcal == Decimal('72.00')
        assert imported_food.kcal_grams == Decimal('50.00')


def test_recipe_import_fills_null_details_on_existing_food(space_1, space_2, u1_s1, u1_s2):
    with scope(space=space_2):
        FoodFactory(space=space_2, name='Egg')

    with scope(space=space_1):
        food = FoodFactory(
            space=space_1,
            name='Egg',
            shopping_measure='Dozen',
            ingredient_unit_grams=Decimal('50.00'),
            count_per_pack=12,
            shopping_measure_grams=Decimal('600.00'),
            kcal=Decimal('72.00'),
            kcal_grams=Decimal('50.00'),
        )
        unit = UnitFactory(space=space_1, name='each')
        step = StepFactory(space=space_1, ingredients__count=0)
        step.ingredients.add(Ingredient.objects.create(
            food=food, unit=unit, amount=3, space=space_1,
        ))
        recipe = RecipeFactory(
            space=space_1,
            created_by=auth.get_user(u1_s1),
            internal=True,
            steps__count=0,
            keywords__count=0,
        )
        recipe.steps.add(step)
        payload = _round_trip_payload(recipe)

    request = _request(u1_s2)
    serializer = RecipeExportSerializer(data=payload, context={'request': request})
    assert serializer.is_valid(), serializer.errors
    with scope(space=space_2):
        serializer.save()
        existing = Food.objects.get(name='Egg')
        assert existing.shopping_measure == 'Dozen'
        assert existing.kcal == Decimal('72.00')
        assert existing.kcal_grams == Decimal('50.00')
        assert existing.count_per_pack == 12


def test_recipe_import_does_not_overwrite_existing_food_details(space_1, space_2, u1_s1, u1_s2):
    with scope(space=space_2):
        FoodFactory(
            space=space_2,
            name='Egg',
            kcal=Decimal('10.00'),
            kcal_grams=Decimal('100.00'),
        )

    with scope(space=space_1):
        food = FoodFactory(
            space=space_1,
            name='Egg',
            kcal=Decimal('72.00'),
            kcal_grams=Decimal('50.00'),
        )
        unit = UnitFactory(space=space_1, name='each')
        step = StepFactory(space=space_1, ingredients__count=0)
        step.ingredients.add(Ingredient.objects.create(
            food=food, unit=unit, amount=3, space=space_1,
        ))
        recipe = RecipeFactory(
            space=space_1,
            created_by=auth.get_user(u1_s1),
            internal=True,
            steps__count=0,
            keywords__count=0,
        )
        recipe.steps.add(step)
        payload = _round_trip_payload(recipe)

    request = _request(u1_s2)
    serializer = RecipeExportSerializer(data=payload, context={'request': request})
    assert serializer.is_valid(), serializer.errors
    with scope(space=space_2):
        serializer.save()
        existing = Food.objects.get(name='Egg')
        assert existing.kcal == Decimal('10.00')
        assert existing.kcal_grams == Decimal('100.00')
