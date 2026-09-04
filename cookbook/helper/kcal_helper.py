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


def recipe_kcal_per_serving(recipe):
    if recipe is None:
        return Decimal(0)
    servings = getattr(recipe, 'servings', None) or 1
    try:
        servings = Decimal(servings)
    except (TypeError, ValueError):
        servings = Decimal(1)
    if servings <= 0:
        servings = Decimal(1)
    return recipe_kcal_total(recipe) / servings
