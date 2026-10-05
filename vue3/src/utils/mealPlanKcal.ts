import {MealPlan} from "@/openapi";

export function plannedKcal(plan: MealPlan): number {
    return Number(plan.kcalPerServing ?? 0) * Number(plan.servings ?? 0)
}

export function roundKcal(value: number): number {
    return Math.round(value)
}
