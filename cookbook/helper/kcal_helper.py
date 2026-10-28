from decimal import Decimal

from cookbook.helper.food_pack import ingredient_to_grams, to_decimal


def ingredient_kcal(ingredient):
    """kcal for one recipe ingredient from Food.kcal / Food.kcal_grams, or 0 if unknown."""
    if ingredient is None:
        return Decimal(0)
    if getattr(ingredient, 'no_amount', False):
        return Decimal(0)

    food = getattr(ingredient, 'food', None)
    if food is None:
        return Decimal(0)

    kcal = to_decimal(getattr(food, 'kcal', None))
    kcal_grams = to_decimal(getattr(food, 'kcal_grams', None))
    if kcal is None or kcal_grams is None or kcal_grams <= 0:
        return Decimal(0)

    grams = ingredient_to_grams(ingredient, food)
    if grams is None:
        return Decimal(0)

    return grams * (kcal / kcal_grams)


def recipe_kcal_total(recipe):
    if recipe is None:
        return Decimal(0)
    total = Decimal(0)
    for step in recipe.steps.all():
        for ingredient in step.ingredients.all():
            total += ingredient_kcal(ingredient)
    return total


def _recipe_servings(recipe):
    servings = getattr(recipe, 'servings', None) or 1
    try:
        servings = Decimal(servings)
    except (TypeError, ValueError):
        servings = Decimal(1)
    if servings <= 0:
        servings = Decimal(1)
    return servings


def recipe_kcal_per_serving(recipe):
    if recipe is None:
        return Decimal(0)
    return recipe_kcal_total(recipe) / _recipe_servings(recipe)


def recipe_grams_total(recipe):
    """
    Sum ingredient grams for the recipe, or None when weight cannot be determined
    accurately (any amount-bearing ingredient fails conversion, or none contribute).
    Headers / no_amount lines are skipped.
    """
    if recipe is None:
        return None
    total = Decimal(0)
    saw_amount = False
    for step in recipe.steps.all():
        for ingredient in step.ingredients.all():
            if getattr(ingredient, 'no_amount', False) or getattr(ingredient, 'is_header', False):
                continue
            saw_amount = True
            grams = ingredient_to_grams(ingredient)
            if grams is None:
                return None
            total += grams
    if not saw_amount:
        return None
    return total


def recipe_grams_per_serving(recipe):
    """Grams per serving, or None when total weight cannot be calculated accurately."""
    total = recipe_grams_total(recipe)
    if total is None:
        return None
    return total / _recipe_servings(recipe)
