<template>
    <model-editor-base
        :loading="loading"
        :dialog="dialog"
        @save="saveObject().then((obj:MealPlan) => { useMealPlanStore().plans.set(obj.id, obj);})"
        @delete="useMealPlanStore().plans.delete(editingObj.id); deleteObject()"
        @close="emit('close'); editingObjChanged = false"
        :is-update="isUpdate()"
        :is-changed="editingObjChanged"
        :model-class="modelClass"
        :object-name="editingObjName()"
        :editing-object="editingObj">

        <v-card-text class="pa-0">
            <v-tabs v-model="tab" :disabled="loading" grow>
                <v-tab prepend-icon="$mealplan" value="plan">{{ $t('Meal_Plan') }}</v-tab>
                <v-tab prepend-icon="$shopping" value="shopping" :disabled="!isUpdate()">{{ $t('Shopping_list') }}</v-tab>
            </v-tabs>
        </v-card-text>

        <v-card-text>
            <v-tabs-window v-model="tab">
                <v-tabs-window-item value="plan">
                    <v-form :disabled="loading">

                        <v-row>
                            <v-col cols="12" md="6">
                                <v-text-field
                                    v-if="!editingObj.recipe"
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
                                    v-if="!editingObj.recipe"
                                    class="border rounded mt-1"
                                    density="compact"
                                    max-height="280"
                                    style="overflow-y: auto"
                                >
                                    <v-list-subheader>{{ recipeChoices.length }} {{ $t('Recipes') }}</v-list-subheader>
                                    <v-list-item
                                        v-for="r in recipeChoices"
                                        :key="r.id"
                                        :title="r.name"
                                        @click="selectRecipe(r)"
                                    >
                                        <template #prepend>
                                            <v-avatar size="32" :image="r.image" v-if="r.image"></v-avatar>
                                        </template>
                                    </v-list-item>
                                    <v-list-item v-if="recipeLoading && recipeChoices.length === 0" title="…" disabled></v-list-item>
                                    <v-list-item v-else-if="!recipeLoading && recipeChoices.length === 0" :title="$t('No_Results')" disabled></v-list-item>
                                </v-list>
                                <recipe-card :recipe="editingObj.recipe" :servings="editingObj.servings" v-if="editingObj && editingObj.recipe" link-target="_blank"></recipe-card>
                                <v-btn variant="text" size="small" class="mt-1" v-if="editingObj.recipe" @click="clearRecipe">{{ $t('Clear') }}</v-btn>
                                <v-btn prepend-icon="$shopping" color="create" class="mt-1" v-if="!editingObj.shopping && editingObj.recipe && isUpdate()">
                                    {{ $t('Add') }}
                                    <add-to-shopping-dialog :recipe="editingObj.recipe" :meal-plan="editingObj"
                                                            @created="editingObj.shopping = true;"></add-to-shopping-dialog>
                                </v-btn>

                                <v-checkbox :label="$t('AddToShopping')" v-model="editingObj.addshopping" hide-details v-if="editingObj.recipe && !isUpdate()"></v-checkbox>
                            </v-col>
                            <v-col cols="12" md="6">
                                <v-text-field :label="$t('Title')" v-model="editingObj.title"></v-text-field>
                                <v-row no-gutters class="datetime-joined-group">
                                    <v-col cols="12" sm="7">
                                        <v-date-input
                                            v-model="dateRangeValue"
                                            @update:modelValue="updateDate()"
                                            :first-day-of-week="useUserPreferenceStore().deviceSettings.mealplan_startingDayOfWeek"
                                            :show-week="useUserPreferenceStore().deviceSettings.mealplan_displayWeekNumbers"
                                            :label="$t('Date')"
                                            multiple="range"
                                            prepend-icon=""
                                            prepend-inner-icon="$calendar"
                                            hide-details
                                        ></v-date-input>
                                    </v-col>
                                    <v-col cols="12" sm="5">
                                        <v-text-field v-model="mealPlanTime"
                                            :active="timePickerMenu" :focus="timePickerMenu"
                                            :label="$t('Time')" prepend-inner-icon="fa-solid fa-clock" readonly
                                            hide-details>
                                            <v-menu v-model="timePickerMenu" :close-on-content-click="false"
                                                    activator="parent" transition="scale-transition">
                                                <v-time-picker v-if="timePickerMenu" format="24hr"
                                                               v-model="mealPlanTime"
                                                               @update:modelValue="applyTimeToEditingDates"></v-time-picker>
                                            </v-menu>
                                        </v-text-field>
                                    </v-col>
                                </v-row>

                                <v-input>
                                    <v-btn-group elevation="1" class="w-100" divided border>
                                        <v-btn class="w-25" @click="adjustDateRangeLength(dateRangeValue,-1); updateDate()"><i class="fa-solid fa-minus"></i></v-btn>
                                        <v-btn class="w-25" @click="dateRangeValue = shiftDateRange(dateRangeValue, -1); updateDate()"><i class="fa-solid fa-angles-left"></i>
                                        </v-btn>
                                        <v-btn class="w-25" @click="dateRangeValue = shiftDateRange(dateRangeValue, +1); updateDate()"><i class="fa-solid fa-angles-right"></i>
                                        </v-btn>
                                        <v-btn class="w-25" @click="adjustDateRangeLength(dateRangeValue,+1); updateDate()"><i class="fa-solid fa-plus"></i></v-btn>
                                    </v-btn-group>
                                </v-input>

                                <div class="mb-4">
                                    <div class="text-subtitle-2 mb-1">{{ $t('Meal_Type') }}</div>
                                    <div class="text-caption text-medium-emphasis mb-2">{{ $t('MealTypeHelp') }}</div>
                                    <v-chip-group
                                        :model-value="editingObj.mealType?.id"
                                        @update:model-value="selectMealTypeById"
                                        column
                                    >
                                        <v-chip
                                            v-for="mt in mealTypes"
                                            :key="mt.id"
                                            :value="mt.id"
                                            filter
                                            variant="outlined"
                                        >{{ mt.name }}</v-chip>
                                    </v-chip-group>
                                </div>
                                <v-number-input control-variant="split" :min="0" v-model="editingObj.servings" :label="$t('Servings')" :precision="2"></v-number-input>
                            </v-col>

                        </v-row>
                        <v-row dense>
                            <v-col cols="12">
                                <v-textarea :label="$t('Note')" v-model="editingObj.note" rows="3"></v-textarea>
                            </v-col>
                        </v-row>

                        <closable-help-alert :text="$t('HouseholdSettingsHelp')" :title="$t('Household')"></closable-help-alert>

                    </v-form>
                </v-tabs-window-item>

                <v-tabs-window-item value="shopping">
                    <closable-help-alert class="mb-2" :text="$t('MealPlanShoppingHelp')"></closable-help-alert>

                    <shopping-list-view :meal-plan-id="editingObj.id"></shopping-list-view>

                </v-tabs-window-item>
            </v-tabs-window>
        </v-card-text>
    </model-editor-base>

</template>

<script setup lang="ts">

import {nextTick, onMounted, onUnmounted, PropType, ref, toRaw, watch} from "vue";
import {ApiApi, MealPlan, MealType, RecipeOverview} from "@/openapi";
import ModelEditorBase from "@/components/model_editors/ModelEditorBase.vue";
import {useModelEditorFunctions} from "@/composables/useModelEditorFunctions";
import {DateTime} from "luxon";
import {adjustDateRangeLength, shiftDateRange} from "@/utils/date_utils";
import {useDebounceFn} from "@vueuse/core";
import RecipeCard from "@/components/display/RecipeCard.vue";
import {VDateInput} from "vuetify/components/VDateInput";
import {useUserPreferenceStore} from "@/stores/UserPreferenceStore";
import {ErrorMessageType, MessageType, useMessageStore} from "@/stores/MessageStore";
import {useShoppingStore} from "@/stores/ShoppingStore";
import ClosableHelpAlert from "@/components/display/ClosableHelpAlert.vue";
import {useMealPlanStore} from "@/stores/MealPlanStore";
import AddToShoppingDialog from "@/components/dialogs/AddToShoppingDialog.vue";
import ShoppingListView from "@/components/display/ShoppingListView.vue";

const props = defineProps({
    item: {type: {} as PropType<MealPlan>, required: false, default: null},
    itemDefaults: {type: {} as PropType<MealPlan>, required: false, default: {} as MealPlan},
    itemId: {type: [Number, String], required: false, default: undefined},
    dialog: {type: Boolean, default: false}
})

const emit = defineEmits(['create', 'save', 'delete', 'close', 'changedState'])
const {
    setupState,
    deleteObject,
    saveObject,
    isUpdate,
    editingObjName,
    applyItemDefaults,
    loading,
    editingObj,
    editingObjChanged,
    modelClass
} = useModelEditorFunctions<MealPlan>('MealPlan', emit)

/**
 * watch prop changes and re-initialize editor
 * required to embed editor directly into pages and be able to change item from the outside
 */
watch([() => props.item, () => props.itemId], () => {
    initializeEditor()
})

// object specific data (for selects/display)
const tab = ref('plan')

const dateRangeValue = ref([] as Date[])
const timePickerMenu = ref(false)
const mealPlanTime = ref('12:00')
const recipeQuery = ref('')
const recipeChoices = ref([] as RecipeOverview[])
const recipeLoading = ref(false)
const mealTypes = ref([] as MealType[])

const DEFAULT_MEAL_TYPE_SEED = [
    {name: 'Breakfast', order: 0, time: '08:00:00', color: '#ddbf86'},
    {name: 'Lunch', order: 1, time: '12:00:00', color: '#82aa8b'},
    {name: 'Dinner', order: 2, time: '18:00:00', color: '#385f84'},
]

function selectMealTypeById(id: number | null) {
    const mealType = mealTypes.value.find((mt) => mt.id === id)
    if (mealType) {
        editingObj.value.mealType = mealType
    }
}

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
        mealTypes.value = results
        if (!editingObj.value.mealType && results.length > 0) {
            const preferred = useUserPreferenceStore().userSettings.defaultMealType
            editingObj.value.mealType = results.find((mt) => mt.id === preferred?.id) ?? results[0]
        }
    }).catch((err: any) => {
        useMessageStore().addError(ErrorMessageType.FETCH_ERROR, err)
        mealTypes.value = []
    })
}

function selectRecipe(recipe: RecipeOverview) {
    editingObj.value.recipe = recipe
    editingObj.value.servings = recipe.servings ?? 1
    recipeQuery.value = recipe.name
}

function clearRecipe() {
    editingObj.value.recipe = undefined
    recipeQuery.value = ''
    searchRecipes()
}

function searchRecipes() {
    recipeLoading.value = true
    const api = new ApiApi()
    return api.apiRecipeList({query: recipeQuery.value || '', page: 1, pageSize: 25}).then((r) => {
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
    if (editingObj.value.recipe && value === editingObj.value.recipe.name) {
        return
    }
    if (editingObj.value.recipe && value !== editingObj.value.recipe.name) {
        editingObj.value.recipe = undefined
    }
    debouncedSearchRecipes()
})

watch(() => editingObj.value.mealType, (newType, oldType) => {
    if (newType?.time && newType?.time !== oldType?.time) {
        mealPlanTime.value = newType.time.substring(0, 5)
        applyTimeToEditingDates()
    }
})

function applyTimeToEditingDates() {
    if (!mealPlanTime.value) return
    let changed = editingObjChanged.value
    const [hours, minutes] = mealPlanTime.value.split(':').map(Number)
    if (editingObj.value.fromDate) {
        editingObj.value.fromDate = DateTime.fromJSDate(editingObj.value.fromDate)
            .set({hour: hours, minute: minutes, second: 0, millisecond: 0}).toJSDate()
    }
    if (editingObj.value.toDate) {
        editingObj.value.toDate = DateTime.fromJSDate(editingObj.value.toDate)
            .set({hour: hours, minute: minutes, second: 0, millisecond: 0}).toJSDate()
    }
    nextTick(() => {
        editingObjChanged.value = changed
    })
}

/**
 * update shopping list when switching to shopping tab
 */
watch(() => tab.value, (newVal, oldVal) => {
    if (newVal == 'shopping') {
        useShoppingStore().selectedMealPlan = editingObj.value.id
        useShoppingStore().updateEntriesStructure()
    }
})

onMounted(() => {
    initializeEditor()
})

onUnmounted(() => {
    if (useShoppingStore().selectedMealPlan == editingObj.value.id) {
        useShoppingStore().selectedMealPlan = undefined
    }
})

/**
 * component specific state setup logic
 */
function initializeEditor() {
    const api = new ApiApi()

    // load meal types and create new object based on default type when initially loading
    // TODO remove this once moved to user preference from MealType property
    loading.value = true

    setupState(props.item, props.itemId, {
        newItemFunction: () => {
            const noonToday = DateTime.now().set({hour: 12, minute: 0, second: 0, millisecond: 0})
            editingObj.value.fromDate = noonToday.toJSDate()
            editingObj.value.toDate = noonToday.toJSDate()
            mealPlanTime.value = '12:00'

            editingObj.value.servings = 1

            if (useUserPreferenceStore().userSettings.defaultMealType){
                editingObj.value.mealType = useUserPreferenceStore().userSettings.defaultMealType
            }

            editingObj.value.addshopping = useUserPreferenceStore().userSettings.mealplanAutoaddShopping

            applyItemDefaults(props.itemDefaults)

            if (editingObj.value.mealType?.time) {
                mealPlanTime.value = editingObj.value.mealType.time.substring(0, 5)
            }
            applyTimeToEditingDates()

            if (editingObj.value.toDate < editingObj.value.fromDate) {
                editingObj.value.toDate = editingObj.value.fromDate
            }

            initializeDateRange()

            recipeQuery.value = editingObj.value.recipe?.name ?? ''
            if (!editingObj.value.recipe) {
                searchRecipes()
            }
            loadMealTypes()

            nextTick(() => {
                editingObjChanged.value = false
            })
        }, existingItemFunction: () => {
            editingObj.value = structuredClone(toRaw(editingObj.value))
            if (editingObj.value.fromDate) {
                mealPlanTime.value = DateTime.fromJSDate(editingObj.value.fromDate).toFormat('HH:mm')
            }
            initializeDateRange()
            recipeQuery.value = editingObj.value.recipe?.name ?? ''
            if (!editingObj.value.recipe) {
                searchRecipes()
            }
            loadMealTypes()
        }
    },)

}

/**
 * update the editing object with data from the date range selector whenever its changed (could probably be a watcher)
 */
// TODO properly hook into beforeSave hook if i ever implement one for model editors
function updateDate() {
    if (dateRangeValue.value != null) {
        editingObj.value.fromDate = dateRangeValue.value[0]
        if (dateRangeValue.value[dateRangeValue.value.length - 1] > editingObj.value.fromDate) {
            editingObj.value.toDate = dateRangeValue.value[dateRangeValue.value.length - 1]
        } else {
            editingObj.value.toDate = editingObj.value.fromDate
        }
        applyTimeToEditingDates()
    } else {
        useMessageStore().addMessage(MessageType.WARNING, 'Missing Date', 7000)
    }
}

/**
 * initialize the dateRange selector when the editingObject is initialized
 */
function initializeDateRange() {
    if (editingObj.value.toDate && DateTime.fromJSDate(editingObj.value.toDate).diff(DateTime.fromJSDate(editingObj.value.fromDate), 'days').toObject().days! >= 1) {
        dateRangeValue.value = [editingObj.value.fromDate]
        let currentDate = DateTime.fromJSDate(editingObj.value.fromDate).plus({day: 1}).toJSDate()
        while (currentDate <= editingObj.value.toDate) {
            dateRangeValue.value.push(currentDate)
            currentDate = DateTime.fromJSDate(currentDate).plus({day: 1}).toJSDate()
        }
    } else {
        dateRangeValue.value = [editingObj.value.fromDate, editingObj.value.fromDate]
    }
}

</script>

<style scoped>
@media (min-width: 600px) {
    .datetime-joined-group {
        background: rgba(0, 0, 0, 0.04);
        border-radius: 4px 4px 0 0;
    }
    .datetime-joined-group :deep(.v-field__overlay) {
        display: none;
    }
    .datetime-joined-group :deep(.v-field) {
        border-radius: 0;
    }
    .datetime-joined-group > :first-child :deep(.v-field) {
        border-top-left-radius: 4px;
    }
    .datetime-joined-group > :last-child :deep(.v-field) {
        border-top-right-radius: 4px;
    }
}
</style>