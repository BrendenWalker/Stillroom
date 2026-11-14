/**
 * Shopping list stores amount_grams. When shopping_measure_grams is set,
 * the trip list shows ceil(grams / smg) shopping units with a small relative
 * pack tolerance (what to buy); editors show exact grams / smg (what the recipes need).
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
// oz↔g conversion vs rounded label grams lands ~0.057% over a whole pack
// (15 oz → 425.2424 g vs a 425 g can). Treat that as one pack, not two.
const PACK_COUNT_REL_EPS = 0.001

export function inStoreShoppingCountDisplay(grams: unknown, shoppingMeasureGrams: unknown): number {
    const g = parsePackNumber(grams)
    if (g == null) return 0
    const m = parseShoppingMeasureGrams(shoppingMeasureGrams)
    if (m == null) return Math.ceil(g - CEIL_EPS)
    // Multiply (not subtract) so N cans of conversion noise stay within tolerance of N packs.
    const units = g / m
    if (units <= 0) return 0
    return Math.ceil(units * (1 - PACK_COUNT_REL_EPS))
}

export function formatGramsLabel(grams: unknown): string {
    const n = parsePackNumber(grams)
    if (n == null || n <= 0) return ''
    // Display only: oz↔g noise (e.g. 425.2424) rounds to whole grams for the shopping label.
    return `${Math.round(n)} g`
}

export function shoppingUnitsToGrams(units: unknown, shoppingMeasureGrams: unknown): number | null {
    const u = parsePackNumber(units)
    const m = parseShoppingMeasureGrams(shoppingMeasureGrams)
    if (u == null || m == null) return null
    return u * m
}

export type ConsumePackAction<T> = {
    entry: T
    boughtGrams: number
    leftoverGrams: number
}

export type ShoppingGramsEntry = {
    checked?: boolean
    amountGrams?: number | null
}

export function planConsumePackGrams<T extends ShoppingGramsEntry>(
    entries: T[],
    packGrams: unknown,
): ConsumePackAction<T>[] {
    let remaining = parsePackNumber(packGrams)
    if (remaining == null || remaining <= 0) return []

    const actions: ConsumePackAction<T>[] = []
    for (const entry of entries) {
        if (remaining <= 0) break
        if (entry.checked) continue
        const grams = parsePackNumber(entry.amountGrams)
        if (grams == null || grams <= 0) continue
        if (grams <= remaining) {
            actions.push({entry, boughtGrams: grams, leftoverGrams: 0})
            remaining -= grams
        } else {
            actions.push({entry, boughtGrams: remaining, leftoverGrams: grams - remaining})
            remaining = 0
            break
        }
    }
    return actions
}
