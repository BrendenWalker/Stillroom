import json
from decimal import Decimal

import pytest
from django.contrib import auth
from django.urls import reverse
from django_scopes import scope

from cookbook.helper.food_pack import in_store_shopping_count
from cookbook.models import ShoppingListEntry
from cookbook.tests.factories import FoodFactory, IngredientFactory, RecipeFactory, StepFactory, UnitFactory

FOOD_DETAIL_URL = 'api:food-detail'
SHOPPING_LIST_URL = 'api:shoppinglistentry-list'
SHOPPING_FOOD_URL = 'api:food-shopping'
SHOPPING_RECIPE_URL = 'api:recipe-shopping'
SHOPPING_LIST_RECIPE_URL = 'api:shoppinglistrecipe-detail'


@pytest.fixture()
def packed_eggs(space_1):
    return FoodFactory(
        space=space_1,
        shopping_measure='dozen',
        ingredient_unit_grams=Decimal('50'),
        count_per_pack=12,
        shopping_measure_grams=Decimal('600'),
    )


def test_food_api_derives_shopping_measure_grams(u1_s1, space_1):
    with scope(space=space_1):
        food = FoodFactory(space=space_1)
    r = u1_s1.patch(
        reverse(FOOD_DETAIL_URL, args={food.id}),
        {
            'shopping_measure': 'dozen',
            'ingredient_unit_grams': 50,
            'count_per_pack': 12,
            'shopping_measure_grams': 1,
        },
        content_type='application/json',
    )
    assert r.status_code == 200
    body = json.loads(r.content)
    assert float(body['shopping_measure_grams']) == 600
    assert body['shopping_measure'] == 'dozen'
    assert body['count_per_pack'] == 12


def test_food_api_count_per_pack_one_fills_missing_grams(u1_s1, space_1):
    with scope(space=space_1):
        food = FoodFactory(space=space_1)
    r = u1_s1.patch(
        reverse(FOOD_DETAIL_URL, args={food.id}),
        {
            'count_per_pack': 1,
            'shopping_measure_grams': 50,
        },
        content_type='application/json',
    )
    assert r.status_code == 200
    body = json.loads(r.content)
    assert float(body['ingredient_unit_grams']) == 50
    assert float(body['shopping_measure_grams']) == 50


def test_food_api_count_per_pack_must_be_at_least_one(u1_s1, space_1):
    with scope(space=space_1):
        food = FoodFactory(space=space_1)
    r = u1_s1.patch(
        reverse(FOOD_DETAIL_URL, args={food.id}),
        {'count_per_pack': 0},
        content_type='application/json',
    )
    assert r.status_code == 400


def test_manual_add_uses_one_shopping_unit(u1_s1, packed_eggs):
    r = u1_s1.put(reverse(SHOPPING_FOOD_URL, args={packed_eggs.id}))
    assert r.status_code == 204
    entries = json.loads(u1_s1.get(reverse(SHOPPING_LIST_URL)).content)['results']
    assert len(entries) == 1
    assert float(entries[0]['amount_grams']) == 600
    assert float(entries[0]['amount']) == 1
    assert entries[0]['unit'] is None
    assert entries[0]['food']['shopping_measure'] == 'dozen'


def test_recipe_adds_required_grams(u1_s1, space_1, packed_eggs):
    user = auth.get_user(u1_s1)
    with scope(space=space_1):
        each = UnitFactory(space=space_1, name='each')
        recipe = RecipeFactory(space=space_1, created_by=user, servings=1, steps__count=0, keywords__count=0)
        step = StepFactory(space=space_1, ingredients__count=0)
        recipe.steps.add(step)
        ing = IngredientFactory(space=space_1, food=packed_eggs, unit=each, amount=3)
        step.ingredients.add(ing)

    r = u1_s1.put(reverse(SHOPPING_RECIPE_URL, args={recipe.id}))
    assert r.status_code == 200
    entries = json.loads(u1_s1.get(reverse(SHOPPING_LIST_URL)).content)['results']
    assert len(entries) == 1
    assert float(entries[0]['amount_grams']) == 150
    assert abs(float(entries[0]['amount']) - 0.25) < 0.0001
    assert in_store_shopping_count(entries[0]['amount_grams'], packed_eggs.shopping_measure_grams) == 1


def test_recipe_count_unit_aliases_convert_to_grams(u1_s1, space_1, packed_eggs):
    user = auth.get_user(u1_s1)
    with scope(space=space_1):
        eggs = UnitFactory(space=space_1, name='eggs')
        recipe = RecipeFactory(space=space_1, created_by=user, servings=1, steps__count=0, keywords__count=0)
        step = StepFactory(space=space_1, ingredients__count=0)
        recipe.steps.add(step)
        ing = IngredientFactory(space=space_1, food=packed_eggs, unit=eggs, amount=3)
        step.ingredients.add(ing)

    r = u1_s1.put(reverse(SHOPPING_RECIPE_URL, args={recipe.id}))
    assert r.status_code == 200
    entries = json.loads(u1_s1.get(reverse(SHOPPING_LIST_URL)).content)['results']
    assert float(entries[0]['amount_grams']) == 150


def test_foods_without_pack_fields_copy_amount_unit(u1_s1, space_1):
    user = auth.get_user(u1_s1)
    with scope(space=space_1):
        food = FoodFactory(space=space_1)
        unit = UnitFactory(space=space_1, name='cup')
        recipe = RecipeFactory(space=space_1, created_by=user, servings=1, steps__count=0, keywords__count=0)
        step = StepFactory(space=space_1, ingredients__count=0)
        recipe.steps.add(step)
        ing = IngredientFactory(space=space_1, food=food, unit=unit, amount=2)
        step.ingredients.add(ing)

    r = u1_s1.put(reverse(SHOPPING_RECIPE_URL, args={recipe.id}))
    assert r.status_code == 200
    entries = json.loads(u1_s1.get(reverse(SHOPPING_LIST_URL)).content)['results']
    assert len(entries) == 1
    assert entries[0]['amount_grams'] is None
    assert float(entries[0]['amount']) == 2
    assert entries[0]['unit']['name'] == 'cup'


def test_servings_rescale_updates_amount_grams(u1_s1, space_1, packed_eggs):
    user = auth.get_user(u1_s1)
    with scope(space=space_1):
        each = UnitFactory(space=space_1, name='each')
        recipe = RecipeFactory(space=space_1, created_by=user, servings=1, steps__count=0, keywords__count=0)
        step = StepFactory(space=space_1, ingredients__count=0)
        recipe.steps.add(step)
        ing = IngredientFactory(space=space_1, food=packed_eggs, unit=each, amount=3)
        step.ingredients.add(ing)

    r = u1_s1.put(reverse(SHOPPING_RECIPE_URL, args={recipe.id}))
    assert r.status_code == 200
    entries = json.loads(u1_s1.get(reverse(SHOPPING_LIST_URL)).content)['results']
    slr_id = entries[0]['list_recipe']

    r = u1_s1.patch(
        reverse(SHOPPING_LIST_RECIPE_URL, args={slr_id}),
        {'servings': 2},
        content_type='application/json',
    )
    assert r.status_code == 200
    with scope(space=space_1):
        sle = ShoppingListEntry.objects.get(id=entries[0]['id'])
        assert sle.amount_grams == Decimal('300')
        assert abs(sle.amount - Decimal('0.5')) < Decimal('0.0001')


def test_patch_amount_as_shopping_units_updates_grams(u1_s1, packed_eggs):
    r = u1_s1.put(reverse(SHOPPING_FOOD_URL, args={packed_eggs.id}))
    assert r.status_code == 204
    entries = json.loads(u1_s1.get(reverse(SHOPPING_LIST_URL)).content)['results']
    entry_id = entries[0]['id']

    r = u1_s1.patch(
        reverse('api:shoppinglistentry-detail', args={entry_id}),
        {'amount': 2},
        content_type='application/json',
    )
    assert r.status_code == 200
    body = json.loads(r.content)
    assert float(body['amount']) == 2
    assert float(body['amount_grams']) == 1200
    assert body['unit'] is None
