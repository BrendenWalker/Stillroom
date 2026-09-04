<template>
    <v-navigation-drawer
        v-model="open"
        location="end"
        temporary
        :width="xs ? '100%' : 420"
        :scrim="true"
    >
        <v-toolbar density="compact" :title="title">
            <template #prepend>
                <v-btn icon="$close" @click="open = false"></v-btn>
            </template>
        </v-toolbar>

        <div class="pa-4" v-if="mealType">
            <div class="text-subtitle-2 mb-2">{{ $t('Meal_Plan') }}</div>
            <v-list v-if="existingPlans.length" class="mb-4 border rounded" density="compact">
                <v-list-item v-for="plan in existingPlans" :key="plan.id">
                    <template #prepend>
                        <recipe-image :recipe="plan.recipe ?? undefined" height="36px" width="36px" rounded="sm"></recipe-image>
                    </template>
                    <v-list-item-title>{{ plan.recipe?.name || plan.title }}</v-list-item-title>
                    <v-list-item-subtitle>
                        {{ plan.servings }} · {{ roundKcal(plannedKcal(plan)) }} {{ $t('KCal') }}
                    </v-list-item-subtitle>
                    <template #append>
                        <v-btn icon="$delete" variant="text" size="small" @click="removePlan(plan)"></v-btn>
                    </template>
                </v-list-item>
            </v-list>

            <div class="d-flex keyword-row mb-3" v-if="!selectedRecipe">
                <v-model-select
                    model="Keyword"
                    v-model="keywordIds"
                    multiple
                    chips
                    :return-object="false"
                    :label="$t('Keywords')"
                    hide-details
                    density="compact"
                    class="flex-grow-1 keyword-select"
                ></v-model-select>
                <v-btn-toggle v-model="keywordMode" mandatory divided border class="keyword-toggle" density="compact">
                    <v-btn value="and">AND</v-btn>
                    <v-btn value="or">OR</v-btn>
                </v-btn-toggle>
            </div>

            <v-text-field
                :label="$t('Recipe')"
                :placeholder="$t('Search')"
                v-model="recipeQuery"
                clearable
                hide-details
                autocomplete="off"
                prepend-inner-icon="$recipes"
                :loading="recipeLoading"
                @click:clear="clearRecipe"
            ></v-text-field>
            <v-list
                v-if="!selectedRecipe"
                class="border rounded mt-1"
                density="compact"
                max-height="280"
                style="overflow-y: auto"
            >
                <v-list-item
                    v-for="r in recipeChoices"
                    :key="r.id"
                    @click="selectRecipe(r)"
                >
                    <template #prepend>
                        <v-avatar size="32" :image="r.image" v-if="r.image"></v-avatar>
                    </template>
                    <v-list-item-title class="text-truncate pe-2">{{ r.name }}</v-list-item-title>
                    <template #append>
                        <span class="text-caption text-medium-emphasis text-no-wrap recipe-kcal">
                            {{ roundKcal(Number(r.kcalPerServing ?? 0)) }} {{ $t('KCal') }}
                        </span>
                    </template>
                </v-list-item>
                <v-list-item v-if="recipeLoading && recipeChoices.length === 0" title="…" disabled></v-list-item>
                <v-list-item v-else-if="!recipeLoading && recipeChoices.length === 0" :title="$t('No_Results')" disabled></v-list-item>
            </v-list>

            <div v-if="selectedRecipe" class="mt-4">
                <recipe-image :recipe="selectedRecipe" height="180px" rounded="lg"></recipe-image>
                <div class="text-h6 mt-3">{{ selectedRecipe.name }}</div>
                <v-number-input
                    class="mt-3"
                    control-variant="split"
                    :min="0"
                    v-model="servings"
                    :label="$t('Servings')"
                    :precision="2"
                ></v-number-input>
                <div class="text-subtitle-1 mt-2">
                    {{ roundKcal((selectedRecipe.kcalPerServing ?? 0) * Number(servings || 0)) }} {{ $t('Calories') }}
                </div>
                <v-btn
                    class="mt-4"
                    color="create"
                    prepend-icon="$create"
                    block
                    :loading="adding"
                    :disabled="adding"
                    @click="addPlan"
                >{{ $t('Add') }}</v-btn>
                <v-btn class="mt-2" variant="text" block @click="clearRecipe">{{ $t('Clear') }}</v-btn>
            </div>
        </div>
    </v-navigation-drawer>
</template>

<script setup lang="ts">
import {computed, ref, watch} from "vue";
import {useDisplay} from "vuetify";
import {useDebounceFn} from "@vueuse/core";
import {DateTime} from "luxon";
import {ApiApi, ApiRecipeListRequest, MealPlan, MealType, Recipe, RecipeOverview} from "@/openapi";
import {useMealPlanStore} from "@/stores/MealPlanStore";
import {ErrorMessageType, useMessageStore} from "@/stores/MessageStore";
import RecipeImage from "@/components/display/RecipeImage.vue";
import VModelSelect from "@/components/inputs/VModelSelect.vue";
import {plannedKcal, roundKcal} from "@/utils/mealPlanKcal";

const {xs} = useDisplay()
const open = defineModel<boolean>({default: false})

const props = defineProps<{
    date: DateTime | null
    mealType: MealType | null
    existingPlans: MealPlan[]
}>()

const recipeQuery = ref('')
const recipeChoices = ref([] as RecipeOverview[])
const recipeLoading = ref(false)
const selectedRecipe = ref<Recipe | null>(null)
const servings = ref(1)
const adding = ref(false)
const keywordIds = ref([] as number[])
const keywordMode = ref<'and' | 'or'>('and')

const title = computed(() => {
    const typeName = props.mealType?.name ?? ''
    const dateLabel = props.date ? props.date.toFormat('MMM d') : ''
    return [typeName, dateLabel].filter(Boolean).join(' · ')
})

function planDateTime(): Date {
    const day = props.date ?? DateTime.now()
    const time = props.mealType?.time
    let dt = day.startOf('day')
    if (time) {
        const parts = String(time).split(':').map(Number)
        dt = dt.set({hour: parts[0] || 0, minute: parts[1] || 0, second: 0})
    } else {
        dt = dt.set({hour: 12, minute: 0, second: 0})
    }
    return dt.toJSDate()
}

function searchRecipes() {
    recipeLoading.value = true
    const api = new ApiApi()
    const request: ApiRecipeListRequest = {
        query: recipeQuery.value || '',
        page: 1,
        pageSize: 25,
    }
    if (keywordIds.value.length > 0) {
        if (keywordMode.value === 'and') {
            request.keywordsAnd = keywordIds.value
        } else {
            request.keywords = keywordIds.value
        }
    }
    return api.apiRecipeList(request).then((r) => {
        recipeChoices.value = r.results ?? []
    }).catch((err: any) => {
        useMessageStore().addError(ErrorMessageType.FETCH_ERROR, err)
        recipeChoices.value = []
    }).finally(() => {
        recipeLoading.value = false
    })
}

const debouncedSearchRecipes = useDebounceFn(searchRecipes, 300)

watch(recipeQuery, (value) => {
    if (selectedRecipe.value && value === selectedRecipe.value.name) {
        return
    }
    debouncedSearchRecipes()
})

watch([keywordIds, keywordMode], () => {
    if (!selectedRecipe.value) {
        searchRecipes()
    }
})

watch(open, (isOpen) => {
    if (isOpen) {
        if (keywordIds.value.length > 0) {
            keywordIds.value = []
        }
        if (keywordMode.value !== 'and') {
            keywordMode.value = 'and'
        }
        clearRecipe()
        searchRecipes()
    }
})

function selectRecipe(recipe: RecipeOverview) {
    recipeQuery.value = recipe.name
    servings.value = recipe.servings ?? 1
    const api = new ApiApi()
    recipeLoading.value = true
    api.apiRecipeRetrieve({id: recipe.id!}).then((r) => {
        selectedRecipe.value = r
        servings.value = r.servings ?? recipe.servings ?? 1
    }).catch((err: any) => {
        useMessageStore().addError(ErrorMessageType.FETCH_ERROR, err)
    }).finally(() => {
        recipeLoading.value = false
    })
}

function clearRecipe() {
    selectedRecipe.value = null
    recipeQuery.value = ''
}

function addPlan() {
    if (!selectedRecipe.value || !props.mealType || !props.date) {
        return
    }
    adding.value = true
    const when = planDateTime()
    useMealPlanStore().createObject({
        recipe: selectedRecipe.value as unknown as RecipeOverview,
        mealType: props.mealType,
        servings: servings.value,
        fromDate: when,
        toDate: when,
        title: '',
        note: '',
    } as MealPlan).finally(() => {
        adding.value = false
        clearRecipe()
        searchRecipes()
    })
}

function removePlan(plan: MealPlan) {
    useMealPlanStore().deleteObject(plan)
}
</script>

<style scoped>
.keyword-row {
    gap: 0;
    align-items: stretch;
}

.keyword-select {
    min-width: 0;
}

.keyword-row :deep(.v-field) {
    border-top-right-radius: 0;
    border-bottom-right-radius: 0;
}

.keyword-toggle {
    height: auto !important;
    border-top-left-radius: 0 !important;
    border-bottom-left-radius: 0 !important;
}

.keyword-toggle .v-btn {
    height: 100% !important;
}

.recipe-kcal {
    min-width: 4.75rem;
    text-align: right;
}
</style>
