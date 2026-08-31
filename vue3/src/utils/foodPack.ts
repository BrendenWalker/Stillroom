/**
 * Shopping list stores amount_grams. When shopping_measure_grams is set,
 * the trip list shows ceil(grams / smg) shopping units; editors show exact grams / smg.
 */

export type FoodPackLike = {
    shoppingMeasure?: string | null
    ingredientUnitGrams?: number | null
    countPerPack?: number | null
    shoppingMeasureGrams?: number | null
}

export function parsePackNumber(value: unknown): number | null {
    if (value == null || value === '') return null
    const n = typeof value === 'string' ? parseFloat(value) : Number(value)
    if (!Number.isFinite(n)) return null
    return n
}

export function parseShoppingMeasureGrams(value: unknown): number | null {
    const n = parsePackNumber(value)
    if (n == null || n <= 0) return null
    return n
}

export function hasShoppingPack(food: FoodPackLike | null | undefined): boolean {
    return parseShoppingMeasureGrams(food?.shoppingMeasureGrams) != null
}

export function deriveShoppingMeasureGrams({
    ingredientUnitGrams,
    countPerPack,
    shoppingMeasureGrams,
}: {
    ingredientUnitGrams?: number | string | null
    countPerPack?: number | string | null
    shoppingMeasureGrams?: number | string | null
}): number | null {
    const iug = parsePackNumber(ingredientUnitGrams)
    const cpp = parsePackNumber(countPerPack)
    if (iug != null && cpp != null && iug > 0 && cpp > 0) {
        return Math.round(iug * cpp * 100) / 100
    }
    return parsePackNumber(shoppingMeasureGrams)
}

export function validateCountPerPackOneGrams({
    ingredientUnitGrams,
    countPerPack,
    shoppingMeasureGrams,
}: {
    ingredientUnitGrams?: number | string | null
    countPerPack?: number | string | null
    shoppingMeasureGrams?: number | string | null
}): { ok: true } | { ok: false, message: string } {
    const cppRaw = countPerPack === '' || countPerPack == null ? '' : String(countPerPack).trim()
    if (cppRaw === '') return { ok: true }
    const cpp = parseInt(cppRaw, 10)
    if (Number.isNaN(cpp) || cpp !== 1) return { ok: true }

    const iug = parsePackNumber(ingredientUnitGrams)
    const smg = parsePackNumber(shoppingMeasureGrams)
    const hasI = iug != null
    const hasS = smg != null

    if (!hasI && !hasS) return { ok: true }
    if (!hasI || !hasS) {
        return {
            ok: false,
            message: 'When count per pack is 1, set ingredient unit (grams) and grams in shopping measure to the same value.',
        }
    }
    if (Math.abs(iug! - smg!) > 1e-9) {
        return {
            ok: false,
            message: 'When count per pack is 1, ingredient unit (grams) and grams in shopping measure must match.',
        }
    }
    return { ok: true }
}

export function gramsToDisplayUnits(grams: unknown, shoppingMeasureGrams: unknown): number {
    const g = parsePackNumber(grams)
    if (g == null) return 0
    const m = parseShoppingMeasureGrams(shoppingMeasureGrams)
    if (m == null) return g
    return g / m
}

export function formatShoppingUnitsDisplay(units: number): string {
    if (!Number.isFinite(units)) return ''
    const rounded = Math.round(units * 10000) / 10000
    if (Math.abs(rounded - Math.round(rounded)) < 1e-9) return String(Math.round(rounded))
    return String(rounded)
}

const CEIL_EPS = 1e-9

export function inStoreShoppingCountDisplay(grams: unknown, shoppingMeasureGrams: unknown): number {
    const g = parsePackNumber(grams)
    if (g == null) return 0
    const m = parseShoppingMeasureGrams(shoppingMeasureGrams)
    if (m == null) return Math.ceil(g - CEIL_EPS)
    return Math.ceil(g / m - CEIL_EPS)
}

export function formatGramsLabel(grams: unknown): string {
    const n = parsePackNumber(grams)
    if (n == null || n <= 0) return ''
    const rounded = Math.round(n * 10000) / 10000
    if (Math.abs(rounded - Math.round(rounded)) < 1e-9) return `${Math.round(rounded)} g`
    return `${rounded} g`
}

export function shoppingUnitsToGrams(units: unknown, shoppingMeasureGrams: unknown): number | null {
    const u = parsePackNumber(units)
    const m = parseShoppingMeasureGrams(shoppingMeasureGrams)
    if (u == null || m == null) return null
    return u * m
}
