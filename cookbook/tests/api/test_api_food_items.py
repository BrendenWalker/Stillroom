import json

from django.contrib import auth
from django.urls import reverse
from django_scopes import scopes_disabled

from cookbook.models import Food
from cookbook.tests.factories import FoodFactory, ShoppingListEntryFactory, SupermarketCategoryFactory

FOOD_LIST_URL = 'api:food-list'
CATEGORY_DETAIL_URL = 'api:supermarketcategory-detail'
SHOPPING_DETAIL_URL = 'api:shoppinglistentry-detail'
SHOPPING_BULK_URL = 'api:shoppinglistentry-bulk'


def test_category_is_food_defaults_true(u1_s1, space_1):
    with scopes_disabled():
        cat = SupermarketCategoryFactory(space=space_1)
    r = u1_s1.get(reverse(CATEGORY_DETAIL_URL, args={cat.id}))
    assert r.status_code == 200
    assert json.loads(r.content)['is_food'] is True


def test_category_is_food_can_be_false(u1_s1, space_1):
    with scopes_disabled():
        cat = SupermarketCategoryFactory(space=space_1)
    r = u1_s1.patch(
        reverse(CATEGORY_DETAIL_URL, args={cat.id}),
        {'is_food': False},
        content_type='application/json',
    )
    assert r.status_code == 200
    assert json.loads(r.content)['is_food'] is False


def test_food_list_is_food_filter(u1_s1, space_1):
    prefix = 'zzisfoodfilter'
    with scopes_disabled():
        food_cat = SupermarketCategoryFactory(space=space_1, name=f'{prefix}_produce', is_food=True)
        non_food_cat = SupermarketCategoryFactory(space=space_1, name=f'{prefix}_household', is_food=False)
        uncategorized = FoodFactory(space=space_1, name=f'{prefix}_uncat')
        food_item = FoodFactory(space=space_1, name=f'{prefix}_food', supermarket_category=food_cat)
        non_food_item = FoodFactory(space=space_1, name=f'{prefix}_nonfood', supermarket_category=non_food_cat)

    r = json.loads(u1_s1.get(f'{reverse(FOOD_LIST_URL)}?query={prefix}&is_food=true').content)
    ids = {x['id'] for x in r['results']}
    assert uncategorized.id in ids
    assert food_item.id in ids
    assert non_food_item.id not in ids

    r = json.loads(u1_s1.get(f'{reverse(FOOD_LIST_URL)}?query={prefix}&is_food=false').content)
    ids = {x['id'] for x in r['results']}
    assert non_food_item.id in ids
    assert food_item.id not in ids
    assert uncategorized.id not in ids


def test_shopping_add_onhand_respects_category_is_food(u1_s1, space_1):
    user = auth.get_user(u1_s1)
    user.userpreference.shopping_add_onhand = True
    user.userpreference.save()

    with scopes_disabled():
        food_cat = SupermarketCategoryFactory(space=space_1, is_food=True)
        non_food_cat = SupermarketCategoryFactory(space=space_1, name='household-nf', is_food=False)
        food_item = FoodFactory(space=space_1, supermarket_category=food_cat)
        non_food_item = FoodFactory(space=space_1, supermarket_category=non_food_cat)
        uncategorized = FoodFactory(space=space_1)
        e_food = ShoppingListEntryFactory(space=space_1, created_by=user, food=food_item)
        e_non = ShoppingListEntryFactory(space=space_1, created_by=user, food=non_food_item)
        e_uncat = ShoppingListEntryFactory(space=space_1, created_by=user, food=uncategorized)

    for entry in (e_food, e_non, e_uncat):
        r = u1_s1.patch(
            reverse(SHOPPING_DETAIL_URL, args={entry.id}),
            {'checked': True},
            content_type='application/json',
        )
        assert r.status_code == 200

    with scopes_disabled():
        assert Food.objects.get(id=food_item.id).onhand_users.filter(id=user.id).exists()
        assert not Food.objects.get(id=non_food_item.id).onhand_users.filter(id=user.id).exists()
        assert Food.objects.get(id=uncategorized.id).onhand_users.filter(id=user.id).exists()


def test_shopping_bulk_add_onhand_respects_category_is_food(u1_s1, space_1):
    user = auth.get_user(u1_s1)
    user.userpreference.shopping_add_onhand = True
    user.userpreference.save()

    with scopes_disabled():
        food_cat = SupermarketCategoryFactory(space=space_1, is_food=True)
        non_food_cat = SupermarketCategoryFactory(space=space_1, name='bulk-household', is_food=False)
        food_item = FoodFactory(space=space_1, supermarket_category=food_cat)
        non_food_item = FoodFactory(space=space_1, supermarket_category=non_food_cat)
        e_food = ShoppingListEntryFactory(space=space_1, created_by=user, food=food_item)
        e_non = ShoppingListEntryFactory(space=space_1, created_by=user, food=non_food_item)

    r = u1_s1.post(
        reverse(SHOPPING_BULK_URL),
        {'ids': [e_food.id, e_non.id], 'checked': True},
        content_type='application/json',
    )
    assert r.status_code == 200

    with scopes_disabled():
        assert Food.objects.get(id=food_item.id).onhand_users.filter(id=user.id).exists()
        assert not Food.objects.get(id=non_food_item.id).onhand_users.filter(id=user.id).exists()


INGREDIENT_LIST_URL = 'api:ingredient-list'
INGREDIENT_DETAIL_URL = 'api:ingredient-detail'


def test_ingredient_api_rejects_non_food_item(u1_s1, space_1):
    with scopes_disabled():
        non_food_cat = SupermarketCategoryFactory(space=space_1, name='household-ing', is_food=False)
        sponge = FoodFactory(space=space_1, name='zz-sponge', supermarket_category=non_food_cat)

    r = u1_s1.post(
        reverse(INGREDIENT_LIST_URL),
        {'food': {'name': sponge.name}, 'unit': {'name': 'each'}, 'amount': 1},
        content_type='application/json',
    )
    assert r.status_code == 400
    assert 'food' in json.loads(r.content)


def test_ingredient_api_allows_food_item(u1_s1, space_1):
    with scopes_disabled():
        food_cat = SupermarketCategoryFactory(space=space_1, is_food=True)
        flour = FoodFactory(space=space_1, name='zz-flour', supermarket_category=food_cat)

    r = u1_s1.post(
        reverse(INGREDIENT_LIST_URL),
        {'food': {'name': flour.name}, 'unit': {'name': 'each'}, 'amount': 1},
        content_type='application/json',
    )
    assert r.status_code == 201, r.content


def test_ingredient_api_keeps_existing_non_food_on_unrelated_update(u1_s1, space_1, recipe_1_s1):
    with scopes_disabled():
        non_food_cat = SupermarketCategoryFactory(space=space_1, name='legacy-household', is_food=False)
        sponge = FoodFactory(space=space_1, name='zz-legacy-sponge', supermarket_category=non_food_cat)
        ingredient = recipe_1_s1.steps.first().ingredients.first()
        ingredient.food = sponge
        ingredient.save()

    r = u1_s1.patch(
        reverse(INGREDIENT_DETAIL_URL, args={ingredient.id}),
        {'note': 'keep this sponge'},
        content_type='application/json',
    )
    assert r.status_code == 200, r.content
    assert json.loads(r.content)['note'] == 'keep this sponge'
