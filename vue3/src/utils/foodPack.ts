/**
 * Shopping list stores amount_grams. When shopping_measure_grams is set,
 * the trip list shows ceil(grams / smg) shopping units (what to buy);
 * editors show exact grams / smg (what the recipes need).
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

export function applyFoodPackFields({
    ingredientUnitGrams,
    countPerPack,
    shoppingMeasureGrams,
}: {
    ingredientUnitGrams?: number | string | null
    countPerPack?: number | string | null
    shoppingMeasureGrams?: number | string | null
}): { ingredientUnitGrams: number | null, shoppingMeasureGrams: number | null, error: string | null } {
    const cppRaw = countPerPack === '' || countPerPack == null ? '' : String(countPerPack).trim()
    let iug = parsePackNumber(ingredientUnitGrams)
    let smg = parsePackNumber(shoppingMeasureGrams)

    if (cppRaw !== '') {
        const cpp = parseInt(cppRaw, 10)
        if (Number.isNaN(cpp) || cpp < 1) {
            return { ingredientUnitGrams: iug, shoppingMeasureGrams: smg, error: 'CountPerPackMin' }
        }
        if (cpp === 1) {
            if (iug == null && smg != null && smg > 0) iug = smg
            else if (smg == null && iug != null && iug > 0) smg = iug
        }
    }

    const derived = deriveShoppingMeasureGrams({
        ingredientUnitGrams: iug,
        countPerPack,
        shoppingMeasureGrams: smg,
    })
    return { ingredientUnitGrams: iug, shoppingMeasureGrams: derived, error: null }
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
