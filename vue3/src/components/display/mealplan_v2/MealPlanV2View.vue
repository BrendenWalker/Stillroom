<template>
    <div class="h-100">
    <v-card class="h-100 d-flex flex-column" :loading="useMealPlanStore().loading">
        <v-card-title class="d-flex align-center flex-wrap ga-2">
            <v-btn icon="fa-solid fa-chevron-left" variant="text" @click="shiftWeek(-1)"></v-btn>
            <v-btn icon="fa-solid fa-chevron-right" variant="text" @click="shiftWeek(1)"></v-btn>
            <span class="text-h6">{{ headerTitle }}</span>
            <v-spacer></v-spacer>
            <v-date-input
                v-model="jumpDate"
                prepend-icon=""
                variant="outlined"
                density="compact"
                hide-details
                style="max-width: 220px"
            >
                <template #prepend>
                    <v-btn density="compact" icon="fa-solid fa-calendar-day" variant="plain" @click.stop="goToday"></v-btn>
                </template>
            </v-date-input>
        </v-card-title>

        <v-card-text class="overflow-y-auto flex-grow-1">
            <meal-plan-v2-day-card
                v-for="day in weekDays"
                :key="day.toISODate()"
                :date="day"
                :meal-types="mealTypes"
                :plans="plansForDay(day)"
                :copying="copyingDate === day.toISODate()"
                @add="(mt) => openDrawer(day, mt)"
                @select-plan="(mt) => openDrawer(day, mt)"
                @copy-yesterday="copyYesterday(day)"
            ></meal-plan-v2-day-card>
        </v-card-text>
    </v-card>

        <meal-plan-v2-picker-drawer
            v-model="drawerOpen"
            :date="drawerDate"
            :meal-type="drawerMealType"
            :existing-plans="drawerPlans"
        ></meal-plan-v2-picker-drawer>
    </div>
</template>

<script setup lang="ts">
import {computed, onMounted, ref, watch} from "vue";
import {DateTime} from "luxon";
import {useI18n} from "vue-i18n";
import {VDateInput} from "vuetify/components/VDateInput";
import {ApiApi, MealPlan, MealType} from "@/openapi";
import {useMealPlanStore} from "@/stores/MealPlanStore";
import {useUserPreferenceStore} from "@/stores/UserPreferenceStore";
import {ErrorMessageType, useMessageStore} from "@/stores/MessageStore";
import MealPlanV2DayCard from "./MealPlanV2DayCard.vue";
import MealPlanV2PickerDrawer from "./MealPlanV2PickerDrawer.vue";

const {t, locale} = useI18n()

const DEFAULT_MEAL_TYPE_SEED = [
    {name: 'Breakfast', order: 0, time: '08:00:00', color: '#ddbf86'},
    {name: 'Lunch', order: 1, time: '12:00:00', color: '#82aa8b'},
    {name: 'Dinner', order: 2, time: '18:00:00', color: '#385f84'},
]

const anchorDate = ref(DateTime.now().startOf('day'))
const jumpDate = ref(new Date())
const mealTypes = ref([] as MealType[])
const drawerOpen = ref(false)
const drawerDate = ref<DateTime | null>(null)
const drawerMealType = ref<MealType | null>(null)
const copyingDate = ref<string | null>(null)

function jsWeekdayToLuxon(jsDay: number) {
    return jsDay === 0 ? 7 : jsDay
}

const weekStart = computed(() => {
    const startDow = jsWeekdayToLuxon(useUserPreferenceStore().deviceSettings.mealplan_startingDayOfWeek)
    const start = anchorDate.value.startOf('day')
    const delta = (start.weekday - startDow + 7) % 7
    return start.minus({days: delta})
})

const weekDays = computed(() => {
    return Array.from({length: 7}, (_, i) => weekStart.value.plus({days: i}))
})

const isCurrentWeek = computed(() => weekStart.value.hasSame(weekStartFor(DateTime.now()), 'day'))

const headerTitle = computed(() => {
    if (isCurrentWeek.value) {
        return t('This_Week')
    }
    const first = weekDays.value[0].setLocale(locale.value).toLocaleString(DateTime.DATE_MED)
    const last = weekDays.value[6].setLocale(locale.value).toLocaleString(DateTime.DATE_MED)
    return `${first} – ${last}`
})

function weekStartFor(day: DateTime) {
    const startDow = jsWeekdayToLuxon(useUserPreferenceStore().deviceSettings.mealplan_startingDayOfWeek)
    const start = day.startOf('day')
    const delta = (start.weekday - startDow + 7) % 7
    return start.minus({days: delta})
}

function shiftWeek(delta: number) {
    anchorDate.value = weekStart.value.plus({weeks: delta})
}

function goToday() {
    anchorDate.value = DateTime.now().startOf('day')
    jumpDate.value = new Date()
}

watch(jumpDate, (value) => {
    if (value) {
        anchorDate.value = DateTime.fromJSDate(value).startOf('day')
    }
})

function localDay(date: Date) {
    return DateTime.fromJSDate(date).toLocal().startOf('day')
}

function planCoversDay(plan: MealPlan, day: DateTime) {
    const from = localDay(plan.fromDate)
    const to = localDay(plan.toDate ?? plan.fromDate)
    const d = day.startOf('day')
    return d >= from && d <= to
}

function plansForDay(day: DateTime) {
    return useMealPlanStore().planList.filter((p) => planCoversDay(p, day))
}

const drawerPlans = computed(() => {
    if (!drawerDate.value || !drawerMealType.value) {
        return [] as MealPlan[]
    }
    return plansForDay(drawerDate.value).filter((p) => p.mealType?.id === drawerMealType.value?.id)
})

function openDrawer(day: DateTime, mealType: MealType) {
    drawerDate.value = day
    drawerMealType.value = mealType
    drawerOpen.value = true
}

function refreshWeek() {
    const from = weekStart.value.minus({days: 1}).toJSDate()
    const to = weekStart.value.plus({days: 6, hours: 23}).toJSDate()
    useMealPlanStore().refreshFromAPI(from, to)
}

watch(weekStart, () => {
    refreshWeek()
}, {immediate: true})

function loadMealTypes() {
    const api = new ApiApi()
    return api.apiMealTypeList({page: 1, pageSize: 50}).then(async (r) => {
        let results = r.results ?? []
        if (results.length === 0) {
            for (const seed of DEFAULT_MEAL_TYPE_SEED) {
                await api.apiMealTypeCreate({mealType: seed as MealType})
            }
            results = (await api.apiMealTypeList({page: 1, pageSize: 50})).results ?? []
        }
        mealTypes.value = [...results].sort((a, b) => {
            const at = a.time || ''
            const bt = b.time || ''
            if (at === bt) {
                return (a.id ?? 0) - (b.id ?? 0)
            }
            return at < bt ? -1 : 1
        })
    }).catch((err: any) => {
        useMessageStore().addError(ErrorMessageType.FETCH_ERROR, err)
        mealTypes.value = []
    })
}

function copyDateTime(day: DateTime, mealType: MealType | undefined, source: MealPlan) {
    const time = mealType?.time || source.mealType?.time
    let dt = day.startOf('day')
    if (time) {
        const parts = String(time).split(':').map(Number)
        dt = dt.set({hour: parts[0] || 0, minute: parts[1] || 0, second: 0})
    } else {
        dt = dt.set({hour: 12, minute: 0, second: 0})
    }
    return dt.toJSDate()
}

async function copyYesterday(day: DateTime) {
    const prev = day.minus({days: 1})
    const source = plansForDay(prev)
    const occupied = new Set(plansForDay(day).map((p) => p.mealType?.id).filter((id) => id != null))
    copyingDate.value = day.toISODate()
    try {
        for (const plan of source) {
            const typeId = plan.mealType?.id
            if (typeId != null && occupied.has(typeId)) {
                continue
            }
            const when = copyDateTime(day, plan.mealType, plan)
            await useMealPlanStore().createObject({
                recipe: plan.recipe,
                mealType: plan.mealType,
                servings: plan.servings,
                fromDate: when,
                toDate: when,
                title: plan.title,
                note: plan.note,
            } as MealPlan)
        }
    } finally {
        copyingDate.value = null
    }
}

onMounted(() => {
    loadMealTypes()
})
</script>
