<template>
    <div class="mealplan-v2-slot">
        <div class="text-subtitle-2 text-medium-emphasis mb-2 text-center">{{ mealType.name }}</div>
        <div
            v-for="plan in plans"
            :key="plan.id"
            class="plan-chip mb-2"
            @click="emit('selectPlan', plan)"
        >
            <recipe-image :recipe="plan.recipe ?? undefined" height="48px" width="48px" rounded="sm"></recipe-image>
            <div class="plan-chip-text">
                <div class="text-body-2 text-truncate">{{ planLabel(plan) }}</div>
                <div class="text-caption text-medium-emphasis">{{ roundKcal(plannedKcal(plan)) }} {{ $t('KCal') }}</div>
            </div>
        </div>
        <v-btn
            icon="$create"
            variant="text"
            size="large"
            class="d-flex mx-auto"
            :aria-label="$t('Add')"
            @click="emit('add')"
        ></v-btn>
    </div>
</template>

<script setup lang="ts">
import {MealPlan, MealType} from "@/openapi";
import RecipeImage from "@/components/display/RecipeImage.vue";
import {plannedKcal, roundKcal} from "@/utils/mealPlanKcal";

defineProps<{
    mealType: MealType
    plans: MealPlan[]
}>()

const emit = defineEmits<{
    add: []
    selectPlan: [plan: MealPlan]
}>()

function planLabel(plan: MealPlan) {
    return plan.recipe?.name || plan.title || ''
}
</script>

<style scoped>
.plan-chip {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 4px;
    border-radius: 8px;
    cursor: pointer;
}
.plan-chip:hover {
    background: rgba(0, 0, 0, 0.04);
}
.plan-chip-text {
    min-width: 0;
    flex: 1;
}
</style>
