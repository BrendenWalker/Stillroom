<template>
    <v-card class="mb-4" variant="outlined">
        <v-card-text>
            <div class="d-flex align-center flex-wrap ga-2 mb-4">
                <div>
                    <div class="text-caption text-medium-emphasis">{{ dateLabel }}</div>
                    <div class="text-h6" :class="{'text-error': isToday}">{{ isToday ? $t('Today') : weekdayLabel }}</div>
                </div>
                <v-spacer></v-spacer>
                <div class="d-flex align-center ga-1" :class="{'text-error': dayKcal === 0}">
                    <v-icon v-if="dayKcal === 0" size="small" icon="fa-solid fa-triangle-exclamation"></v-icon>
                    <span class="text-subtitle-1">{{ roundKcal(dayKcal) }} {{ $t('Calories') }}</span>
                </div>
            </div>

            <div class="slot-row">
                <meal-plan-v2-slot
                    v-for="mt in mealTypes"
                    :key="mt.id"
                    :meal-type="mt"
                    :plans="plansFor(mt)"
                    @add="emit('add', mt)"
                    @select-plan="(plan) => emit('selectPlan', mt, plan)"
                ></meal-plan-v2-slot>
            </div>

            <div class="d-flex justify-center mt-4">
                <v-btn
                    variant="outlined"
                    prepend-icon="$copy"
                    :loading="copying"
                    :disabled="copying"
                    @click="emit('copyYesterday')"
                >{{ $t('Copy_Yesterday') }}</v-btn>
            </div>
        </v-card-text>
    </v-card>
</template>

<script setup lang="ts">
import {computed} from "vue";
import {DateTime} from "luxon";
import {useI18n} from "vue-i18n";
import {MealPlan, MealType} from "@/openapi";
import MealPlanV2Slot from "./MealPlanV2Slot.vue";
import {plannedKcal, roundKcal} from "@/utils/mealPlanKcal";

const props = defineProps<{
    date: DateTime
    mealTypes: MealType[]
    plans: MealPlan[]
    copying?: boolean
}>()

const emit = defineEmits<{
    add: [mealType: MealType]
    selectPlan: [mealType: MealType, plan: MealPlan]
    copyYesterday: []
}>()

const {locale} = useI18n()

const isToday = computed(() => props.date.hasSame(DateTime.now(), 'day'))
const dateLabel = computed(() => props.date.setLocale(locale.value).toFormat('MMMM d'))
const weekdayLabel = computed(() => props.date.setLocale(locale.value).toFormat('cccc'))
const dayKcal = computed(() => props.plans.reduce((sum, plan) => sum + plannedKcal(plan), 0))

function plansFor(mealType: MealType) {
    return props.plans.filter((p) => p.mealType?.id === mealType.id)
}
</script>

<style scoped>
.slot-row {
    display: flex;
    gap: 8px;
    overflow-x: auto;
}
.slot-row > * {
    flex: 1 1 0;
    min-width: 120px;
}
</style>
