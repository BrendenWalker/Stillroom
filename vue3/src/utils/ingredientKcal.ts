import type {Food, Ingredient, Unit} from '@/openapi'
import {parsePackNumber} from '@/utils/foodPack'
import {roundKcal} from '@/utils/mealPlanKcal'

/**
 * Keep in sync with cookbook/helper/food_pack.py COUNT_UNIT_NAMES / GRAM_UNIT_NAMES
 * and cookbook/helper/unit_conversion_helper.py CONVERSION_TABLE['weight'].
 */
const COUNT_UNIT_NAMES = new Set([
    'each', 'ea', 'piece', 'pieces', 'pcs', 'pc', 'pce', 'item', 'items',
    'egg', 'eggs',
    'unit', 'units',
    'count', 'whole',
    'stk', 'stück', 'stuck', 'stueck', 'stücke', 'stuecke',
    'stuk', 'stuks',
    'pieza', 'piezas',
    'pezzo', 'pezzi', 'pz',
    'unidade', 'unidades',
    'szt',
    'ks', 'kus',
    'шт', 'штука',
    '个',
])

const GRAM_UNIT_NAMES = new Set(['g', 'gram', 'grams'])

const WEIGHT_TABLE: Record<string, number> = {
    g: 1000,
    kg: 1,
    ounce: 35.274,
    pound: 2.20462,
}

type ConversionLike = {
    food?: string
    unit?: string
    amount?: number | string
}

function unitName(unit: Unit | string | null | undefined): string {
    if (unit == null) return ''
    const name = typeof unit === 'string' ? unit : (unit.name ?? '')
    return String(name).trim().toLowerCase().replace(/\.+$/, '')
}

function numField(obj: object | null | undefined, ...keys: string[]): number | null {
    if (obj == null) return null
    const record = obj as Record<string, unknown>
    for (const key of keys) {
        const n = parsePackNumber(record[key])
        if (n != null) return n
    }
    return null
}

function strField(obj: object | null | undefined, ...keys: string[]): string {
    if (obj == null) return ''
    const record = obj as Record<string, unknown>
    for (const key of keys) {
        const value = record[key]
        if (value != null && value !== '') return String(value)
    }
    return ''
}

function isCountUnit(unit: Unit | null | undefined): boolean {
    if (unit == null) return true
    return COUNT_UNIT_NAMES.has(unitName(unit))
}

function isGramUnitName(name: string | null | undefined): boolean {
    return GRAM_UNIT_NAMES.has(unitName(name))
}

function convertWeightToGrams(baseUnit: string, amount: number): number | null {
    const from = WEIGHT_TABLE[baseUnit]
    const to = WEIGHT_TABLE.g
    if (from == null || to == null) return null
    return amount / (from / to)
}

export function quantityToGrams(
    food: Food | null | undefined,
    amount: number | string | null | undefined,
    unit: Unit | null | undefined,
): number | null {
    const qty = parsePackNumber(amount)
    if (qty == null || food == null) return null

    const base = strField(unit, 'baseUnit', 'base_unit')
    if (base && base in WEIGHT_TABLE) {
        return convertWeightToGrams(base, qty)
    }

    const iug = numField(food, 'ingredientUnitGrams', 'ingredient_unit_grams')
    if (isCountUnit(unit) && iug != null && iug > 0) {
        return qty * iug
    }

    const smg = numField(food, 'shoppingMeasureGrams', 'shopping_measure_grams')
    const shoppingMeasure = strField(food, 'shoppingMeasure', 'shopping_measure').trim().toLowerCase()
    if (unit != null && shoppingMeasure && unitName(unit) === shoppingMeasure && smg != null && smg > 0) {
        return qty * smg
    }

    return null
}

function gramsFromSavedConversions(ingredient: Ingredient): number | null {
    const convs = ingredient.conversions as ConversionLike[] | undefined
    if (!Array.isArray(convs) || convs.length === 0 || ingredient.unit == null) return null

    const currentUnit = unitName(ingredient.unit)
    if (!currentUnit) return null

    const saved = convs.find(c => unitName(c?.unit) === currentUnit)
    const gram = convs.find(c => isGramUnitName(c?.unit))
    const savedAmount = parsePackNumber(saved?.amount)
    const gramAmount = parsePackNumber(gram?.amount)
    if (savedAmount == null || savedAmount === 0 || gramAmount == null) return null

    const current = parsePackNumber(ingredient.amount)
    if (current == null) return null
    return gramAmount * (current / savedAmount)
}

/**
 * Line-total kcal for the editor. Returns 0 when unknown (hide in the UI).
 * Does not divide by recipe servings.
 */
export function ingredientLineKcal(ingredient: Ingredient | null | undefined): number {
    if (ingredient == null || ingredient.isHeader || ingredient.noAmount) return 0

    const food = ingredient.food
    if (food == null) return 0

    const kcal = numField(food, 'kcal')
    const kcalGrams = numField(food, 'kcalGrams', 'kcal_grams')
    if (kcal == null || kcalGrams == null || kcalGrams <= 0) return 0

    const grams = quantityToGrams(food, ingredient.amount, ingredient.unit)
        ?? gramsFromSavedConversions(ingredient)
    if (grams == null) return 0

    return roundKcal(grams * (kcal / kcalGrams))
}
