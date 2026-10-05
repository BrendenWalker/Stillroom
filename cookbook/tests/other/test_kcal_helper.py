from decimal import Decimal

from django.contrib import auth
from django_scopes import scopes_disabled

from cookbook.helper.kcal_helper import ingredient_kcal, recipe_grams_per_serving, recipe_kcal_per_serving
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


def test_ingredient_kcal_from_food_density(space_1, u1_s1):
    user = auth.get_user(u1_s1)
    with scopes_disabled():
        food = Food.objects.create(
            name='eggs',
            space=space_1,
            kcal=Decimal('274'),
            kcal_grams=Decimal('100'),
        )
        recipe = _gram_recipe(space_1, user, food, amount=200, servings=2)
        ingredient = recipe.steps.first().ingredients.first()
        assert ingredient_kcal(ingredient) == Decimal('548')


def test_ingredient_kcal_missing_on_food_is_zero(space_1, u1_s1):
    user = auth.get_user(u1_s1)
    with scopes_disabled():
        food = Food.objects.create(name='unknown', space=space_1)
        recipe = _gram_recipe(space_1, user, food, amount=200, servings=2)
        ingredient = recipe.steps.first().ingredients.first()
        assert ingredient_kcal(ingredient) == Decimal(0)


def test_ingredient_kcal_no_amount_is_zero(space_1, u1_s1):
    user = auth.get_user(u1_s1)
    with scopes_disabled():
        food = Food.objects.create(
            name='eggs',
            space=space_1,
            kcal=Decimal('274'),
            kcal_grams=Decimal('100'),
        )
        recipe = _gram_recipe(space_1, user, food, amount=200, servings=2)
        ingredient = recipe.steps.first().ingredients.first()
        ingredient.no_amount = True
        ingredient.save()
        assert ingredient_kcal(ingredient) == Decimal(0)


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


def test_grams_per_serving_from_ingredients(space_1, u1_s1):
    user = auth.get_user(u1_s1)
    with scopes_disabled():
        food = Food.objects.create(name='flour', space=space_1)
        recipe = _gram_recipe(space_1, user, food, amount=240, servings=2)
        assert recipe_grams_per_serving(recipe) == Decimal('120')


def test_grams_per_serving_incomplete_conversion_is_none(space_1, u1_s1):
    user = auth.get_user(u1_s1)
    with scopes_disabled():
        unit_cup = Unit.objects.create(name='cup', space=space_1)
        food = Food.objects.create(name='mystery', space=space_1)
        recipe = Recipe.objects.create(
            name='incomplete grams',
            servings=2,
            space=space_1,
            created_by=user,
            waiting_time=0,
            working_time=0,
        )
        step = Step.objects.create(instruction='mix', space=space_1)
        step.ingredients.create(amount=1, unit=unit_cup, food=food, space=space_1)
        recipe.steps.add(step)
        assert recipe_grams_per_serving(recipe) is None


def test_grams_per_serving_skips_no_amount_and_headers(space_1, u1_s1):
    user = auth.get_user(u1_s1)
    with scopes_disabled():
        food = Food.objects.create(name='flour', space=space_1)
        recipe = _gram_recipe(space_1, user, food, amount=200, servings=2)
        step = recipe.steps.first()
        step.ingredients.create(amount=0, food=food, space=space_1, no_amount=True, is_header=True, note='Dry')
        assert recipe_grams_per_serving(recipe) == Decimal('100')


def test_grams_per_serving_no_ingredients_is_none(space_1, u1_s1):
    user = auth.get_user(u1_s1)
    with scopes_disabled():
        recipe = Recipe.objects.create(
            name='empty',
            servings=2,
            space=space_1,
            created_by=user,
            waiting_time=0,
            working_time=0,
        )
        assert recipe_grams_per_serving(recipe) is None
