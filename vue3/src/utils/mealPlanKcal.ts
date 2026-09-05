import {MealPlan} from "@/openapi";

export function plannedKcal(plan: MealPlan): number {
    return Number(plan.kcalPerServing ?? 0) * Number(plan.servings ?? 0)
}

export function roundKcal(value: number): number {
    return Math.round(value)
}

export function lineKcalPerServing(kcal: number | null | undefined, recipeServings: number | null | undefined): number {
    const servings = Number(recipeServings ?? 1)
    const denom = servings > 0 ? servings : 1
    return roundKcal(Number(kcal ?? 0) / denom)
}
