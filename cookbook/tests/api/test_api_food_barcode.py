import json

import pytest
from django.contrib import auth
from django.urls import reverse
from django_scopes import scope, scopes_disabled

from cookbook.models import FoodBarcode
from cookbook.tests.conftest import get_random_food, get_random_unit
from cookbook.tests.factories import FoodBarcodeFactory, FoodFactory

LIST_URL = 'api:foodbarcode-list'
DETAIL_URL = 'api:foodbarcode-detail'
MERGE_URL = 'api:food-merge'

UPC_A = '012345678905'
EAN_13 = '0012345678905'
EAN_8 = '96385074'
INVALID_CHECK = '012345678901'


@pytest.fixture()
def obj_1(space_1, u1_s1):
    food = get_random_food(space_1, u1_s1)
    unit = get_random_unit(space_1, u1_s1)
    unit.base_unit = 'g'
    unit.save()
    return FoodBarcode.objects.get_or_create(
        upc=EAN_13,
        food=food,
        brand='Hunt\'s',
        qty=15,
        unit=unit,
        created_by=auth.get_user(u1_s1),
        space=space_1,
    )[0]


@pytest.fixture
def obj_2(space_1, u1_s1):
    food = get_random_food(space_1, u1_s1)
    return FoodBarcode.objects.get_or_create(
        upc=EAN_8,
        food=food,
        created_by=auth.get_user(u1_s1),
        space=space_1,
    )[0]


@pytest.mark.parametrize("arg", [
    ['a_u', 403],
    ['g1_s1', 403],
    ['u1_s1', 200],
    ['a1_s1', 200],
])
def test_list_permission(arg, request):
    c = request.getfixturevalue(arg[0])
    assert c.get(reverse(LIST_URL)).status_code == arg[1]


def test_list_space(obj_1, obj_2, u1_s1, u1_s2, space_2):
    assert json.loads(u1_s1.get(reverse(LIST_URL)).content)['count'] == 2
    assert json.loads(u1_s2.get(reverse(LIST_URL)).content)['count'] == 0

    obj_1.space = space_2
    obj_1.save()

    assert json.loads(u1_s1.get(reverse(LIST_URL)).content)['count'] == 1
    assert json.loads(u1_s2.get(reverse(LIST_URL)).content)['count'] == 1


def test_filter_food_id_and_upc(obj_1, obj_2, u1_s1):
    r = u1_s1.get(reverse(LIST_URL), {'food_id': obj_1.food_id})
    data = json.loads(r.content)
    assert r.status_code == 200
    assert data['count'] == 1
    assert data['results'][0]['id'] == obj_1.id

    r = u1_s1.get(reverse(LIST_URL), {'upc': UPC_A})
    data = json.loads(r.content)
    assert r.status_code == 200
    assert data['count'] == 1
    assert data['results'][0]['upc'] == EAN_13
    assert data['results'][0]['food']['id'] == obj_1.food_id


def test_filter_upc_invalid(u1_s1):
    r = u1_s1.get(reverse(LIST_URL), {'upc': INVALID_CHECK})
    assert r.status_code == 400


@pytest.mark.parametrize("arg", [
    ['a_u', 403],
    ['g1_s1', 403],
    ['u1_s1', 200],
    ['a1_s1', 200],
    ['g1_s2', 403],
    ['u1_s2', 404],
    ['a1_s2', 404],
])
def test_update(arg, request, obj_1):
    c = request.getfixturevalue(arg[0])
    r = c.patch(reverse(DETAIL_URL, args={obj_1.id}), {'brand': 'Store'}, content_type='application/json')
    response = json.loads(r.content)
    assert r.status_code == arg[1]
    if r.status_code == 200:
        assert response['brand'] == 'Store'


@pytest.mark.parametrize("arg", [
    ['a_u', 403],
    ['g1_s1', 403],
    ['u1_s1', 201],
    ['a1_s1', 201],
])
def test_add(arg, request, space_1, u1_s1, u1_s2):
    with scopes_disabled():
        c = request.getfixturevalue(arg[0])
        food = get_random_food(space_1, u1_s1)
        unit = get_random_unit(space_1, u1_s1)
        unit.base_unit = 'g'
        unit.save()
        r = c.post(reverse(LIST_URL), {
            'upc': UPC_A,
            'brand': 'Hunt\'s',
            'qty': 15,
            'unit_id': unit.id,
            'food_id': food.id,
        }, content_type='application/json')
        response = json.loads(r.content)
        assert r.status_code == arg[1]
        if r.status_code == 201:
            assert response['upc'] == EAN_13
            assert response['food']['id'] == food.id
            assert response['unit']['id'] == unit.id
            assert float(response['grams']) == 15
            r = c.get(reverse(DETAIL_URL, args={response['id']}))
            assert r.status_code == 200
            r = u1_s2.get(reverse(DETAIL_URL, args={response['id']}))
            assert r.status_code == 404


def test_add_duplicate_and_checksum(u1_s1, space_1, obj_1):
    r = u1_s1.post(reverse(LIST_URL), {
        'upc': UPC_A,
        'food_id': obj_1.food_id,
        'unit_id': obj_1.unit_id,
    }, content_type='application/json')
    assert r.status_code == 400

    with scopes_disabled():
        food = get_random_food(space_1, u1_s1)
    r = u1_s1.post(reverse(LIST_URL), {
        'upc': INVALID_CHECK,
        'food_id': food.id,
        'unit_id': obj_1.unit_id,
    }, content_type='application/json')
    assert r.status_code == 400


def test_add_requires_unit(u1_s1, space_1):
    with scopes_disabled():
        food = get_random_food(space_1, u1_s1)
    r = u1_s1.post(reverse(LIST_URL), {
        'upc': UPC_A,
        'food_id': food.id,
        'qty': 1,
    }, content_type='application/json')
    assert r.status_code == 400


def test_grams_null_when_unconvertible(u1_s1, space_1):
    with scopes_disabled():
        food = get_random_food(space_1, u1_s1)
        unit = get_random_unit(space_1, u1_s1)
        unit.base_unit = ''
        unit.save()
    r = u1_s1.post(reverse(LIST_URL), {
        'upc': UPC_A,
        'food_id': food.id,
        'qty': 2,
        'unit_id': unit.id,
    }, content_type='application/json')
    assert r.status_code == 201
    assert json.loads(r.content)['grams'] is None


def test_unique_per_space(u1_s1, u1_s2, space_1, space_2, obj_1):
    with scopes_disabled():
        food_2 = FoodFactory(space=space_2)
        unit_2 = get_random_unit(space_2, u1_s2)
    r = u1_s2.post(reverse(LIST_URL), {
        'upc': UPC_A,
        'food_id': food_2.id,
        'unit_id': unit_2.id,
    }, content_type='application/json')
    assert r.status_code == 201
    assert json.loads(r.content)['id'] != obj_1.id


def test_delete(u1_s1, u1_s2, obj_1):
    r = u1_s2.delete(reverse(DETAIL_URL, args={obj_1.id}))
    assert r.status_code == 404

    r = u1_s1.delete(reverse(DETAIL_URL, args={obj_1.id}))
    assert r.status_code == 204
    with scopes_disabled():
        assert not FoodBarcode.objects.filter(pk=obj_1.id).exists()


def test_merge_reassigns_barcodes(u1_s1, space_1):
    with scope(space=space_1):
        source = FoodFactory(space=space_1)
        target = FoodFactory(space=space_1)
        barcode = FoodBarcodeFactory(space=space_1, food=source, created_by=auth.get_user(u1_s1), upc=EAN_13)

    r = u1_s1.put(reverse(MERGE_URL, args=[source.id, target.id]))
    assert r.status_code == 200
    with scope(space=space_1):
        barcode.refresh_from_db()
        assert barcode.food_id == target.id
