from decimal import Decimal

from django.contrib import auth
from django_scopes import scopes_disabled

from cookbook.helper.kcal_helper import recipe_kcal_per_serving
from cookbook.models import Food, Recipe, Step, Unit


def _gram_recipe(space, user, food, amount, servings):
    unit_gram = Unit.objects.create(name='gram', base_unit='g', space=space)
    recipe = Recipe.objects.create(
        name='kcal recipe',
        servings=servings,
        space=space,
        created_by=user,
        waiting_time=0,
        working_time=0,
    )
    step = Step.objects.create(instruction='mix', space=space)
    step.ingredients.create(amount=amount, unit=unit_gram, food=food, space=space)
    recipe.steps.add(step)
    return recipe


def test_kcal_per_serving_from_food_density(space_1, u1_s1):
    user = auth.get_user(u1_s1)
    with scopes_disabled():
        food = Food.objects.create(
            name='eggs',
            space=space_1,
            kcal=Decimal('274'),
            kcal_grams=Decimal('100'),
        )
        recipe = _gram_recipe(space_1, user, food, amount=200, servings=2)
        assert recipe_kcal_per_serving(recipe) == Decimal('274')


def test_kcal_missing_on_food_is_zero(space_1, u1_s1):
    user = auth.get_user(u1_s1)
    with scopes_disabled():
        food = Food.objects.create(name='unknown', space=space_1)
        recipe = _gram_recipe(space_1, user, food, amount=200, servings=2)
        assert recipe_kcal_per_serving(recipe) == Decimal(0)


def test_kcal_zero_servings_does_not_divide_by_zero(space_1, u1_s1):
    user = auth.get_user(u1_s1)
    with scopes_disabled():
        food = Food.objects.create(
            name='eggs',
            space=space_1,
            kcal=Decimal('100'),
            kcal_grams=Decimal('100'),
        )
        recipe = _gram_recipe(space_1, user, food, amount=100, servings=0)
        assert recipe_kcal_per_serving(recipe) == Decimal('100')


def test_kcal_zero_is_valid(space_1, u1_s1):
    user = auth.get_user(u1_s1)
    with scopes_disabled():
        food = Food.objects.create(
            name='water',
            space=space_1,
            kcal=Decimal('0'),
            kcal_grams=Decimal('100'),
        )
        recipe = _gram_recipe(space_1, user, food, amount=200, servings=1)
        assert recipe_kcal_per_serving(recipe) == Decimal(0)
