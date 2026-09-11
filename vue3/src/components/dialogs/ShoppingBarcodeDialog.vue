<template>
    <v-dialog v-model="dialog" max-width="520" :fullscreen="mobile">
        <v-card>
            <v-closable-card-title :title="$t('BarcodeScan')" icon="fa-solid fa-barcode" v-model="dialog"></v-closable-card-title>
            <v-card-text>
                <barcode-scanner v-if="step === 'scan'" @scanned="onScanned"></barcode-scanner>

                <template v-if="step === 'add'">
                    <p>{{ $t('BarcodeAddToListConfirm', {food: pendingFoodName}) }}</p>
                    <v-card-actions class="px-0">
                        <v-spacer></v-spacer>
                        <v-btn variant="text" @click="backToScan">{{ $t('Cancel') }}</v-btn>
                        <v-btn color="create" @click="confirmAdd">{{ $t('AddToShopping') }}</v-btn>
                    </v-card-actions>
                </template>

                <template v-if="step === 'associate'">
                    <p class="mb-2">{{ $t('BarcodeAssociateHelp', {upc: pendingUpc}) }}</p>
                    <v-text-field v-model="associateBrand" :label="$t('Brand')" hide-details class="mb-2"></v-text-field>
                    <v-number-input v-model="associateQty" :label="$t('Amount')" :min="0.0001" :precision="4" control-variant="hidden" hide-details class="mb-2"></v-number-input>
                    <v-model-select :label="$t('Unit')" v-model="associateUnit" model="Unit" class="mb-4"></v-model-select>

                    <v-label class="mb-1">{{ $t('Shopping_list') }}</v-label>
                    <v-list density="compact" class="mb-4" border>
                        <v-list-item
                            v-for="food in listFoods"
                            :key="food.id"
                            :title="food.name"
                            :active="associateFood?.id === food.id"
                            @click="associateFood = food"
                        ></v-list-item>
                        <v-list-item v-if="listFoods.length === 0" :title="$t('Empty')" disabled></v-list-item>
                    </v-list>

                    <v-model-select
                        :label="$t('Food')"
                        model="Food"
                        v-model="associateFood"
                        :list-params="{isFood: true}"
                    ></v-model-select>

                    <v-card-actions class="px-0">
                        <v-spacer></v-spacer>
                        <v-btn variant="text" @click="backToScan">{{ $t('Cancel') }}</v-btn>
                        <v-btn color="create" :disabled="!canAssociate" :loading="saving" @click="confirmAssociate">{{ $t('BarcodeAssociate') }}</v-btn>
                    </v-card-actions>
                </template>
            </v-card-text>
        </v-card>
    </v-dialog>
</template>

<script setup lang="ts">
import {computed, ref, watch} from "vue";
import {useDisplay} from "vuetify";
import {ApiApi, Food, FoodBarcode, FoodSimple, ResponseError, ShoppingListEntry, Unit} from "@/openapi";
import {useShoppingStore} from "@/stores/ShoppingStore";
import {ErrorMessageType, MessageType, useMessageStore} from "@/stores/MessageStore";
import {useI18n} from "vue-i18n";
import {useUserPreferenceStore} from "@/stores/UserPreferenceStore";
import {parsePackNumber} from "@/utils/foodPack";
import VClosableCardTitle from "@/components/dialogs/VClosableCardTitle.vue";
import BarcodeScanner from "@/components/display/BarcodeScanner.vue";
import VModelSelect from "@/components/inputs/VModelSelect.vue";

const {t} = useI18n()
const {mobile} = useDisplay()
const dialog = defineModel<boolean>({default: false})

type Step = 'scan' | 'add' | 'associate'

const step = ref<Step>('scan')
const pendingUpc = ref('')
const pendingFood = ref<Food | FoodSimple | null>(null)
const pendingBarcode = ref<FoodBarcode | null>(null)
const associateFood = ref<Food | FoodSimple | null>(null)
const associateBrand = ref('')
const associateQty = ref(1)
const associateUnit = ref<Unit | null>(null)
const saving = ref(false)
let lastScanAt = 0

const pendingFoodName = computed(() => pendingFood.value?.name || '')
const canAssociate = computed(() => Boolean(associateFood.value?.id && associateUnit.value?.id && Number(associateQty.value) > 0))

const listFoods = computed(() => {
    const byId = new Map<number, FoodSimple>()
    const unchecked: FoodSimple[] = []
    const checked: FoodSimple[] = []
    useShoppingStore().entries.forEach((entry) => {
        const food = entry.food
        if (!food?.id || byId.has(food.id)) {
            return
        }
        byId.set(food.id, food)
        if (entry.checked) {
            checked.push(food)
        } else {
            unchecked.push(food)
        }
    })
    return [...unchecked, ...checked]
})

watch(dialog, (open) => {
    if (open) {
        resetToScan()
    }
})

function resetToScan() {
    step.value = 'scan'
    pendingUpc.value = ''
    pendingFood.value = null
    pendingBarcode.value = null
    associateFood.value = null
    associateBrand.value = ''
    associateQty.value = 1
    associateUnit.value = null
}

function backToScan() {
    resetToScan()
}

function entriesForFood(foodId: number): ShoppingListEntry[] {
    const found: ShoppingListEntry[] = []
    useShoppingStore().entries.forEach((entry) => {
        if (entry.food?.id === foodId) {
            found.push(entry)
        }
    })
    return found
}

async function onScanned(code: string) {
    const now = Date.now()
    if (now - lastScanAt < 1500) {
        return
    }
    lastScanAt = now
    pendingUpc.value = code
    const api = new ApiApi()
    try {
        const result = await api.apiFoodBarcodeList({upc: code})
        if (result.count > 0 && result.results[0].food) {
            await applyKnownFood(result.results[0])
            return
        }
        step.value = 'associate'
    } catch (err) {
        if (err instanceof ResponseError && err.response.status === 400) {
            useMessageStore().addMessage(MessageType.WARNING, {title: t('BarcodeInvalid'), text: code}, 4000)
            return
        }
        useMessageStore().addError(ErrorMessageType.FETCH_ERROR, err)
    }
}

async function applyKnownFood(barcode: FoodBarcode) {
    const food = barcode.food
    pendingFood.value = food
    pendingBarcode.value = barcode
    const packGrams = parsePackNumber(barcode.grams)
    if (packGrams == null || packGrams <= 0) {
        useMessageStore().addMessage(MessageType.WARNING, {title: food.name, text: t('BarcodeNoGrams')}, 4000)
        resetToScan()
        return
    }
    const entries = entriesForFood(food.id!)
    if (entries.length === 0) {
        step.value = 'add'
        return
    }
    const unchecked = entries.filter((e) => !e.checked)
    if (unchecked.length === 0) {
        useMessageStore().addMessage(MessageType.INFO, {title: food.name, text: t('BarcodeAlreadyBought')}, 2500)
        resetToScan()
        return
    }
    const status = await useShoppingStore().consumePackGrams(unchecked, packGrams)
    if (status === 'no_grams') {
        useMessageStore().addMessage(MessageType.WARNING, {title: food.name, text: t('BarcodeListNotInGrams')}, 4000)
    } else {
        useMessageStore().addMessage(MessageType.SUCCESS, {title: food.name, text: t('Completed')}, 2000)
    }
    resetToScan()
}

async function confirmAdd() {
    const foodRef = pendingFood.value
    const packGrams = parsePackNumber(pendingBarcode.value?.grams)
    if (!foodRef?.id) {
        return
    }
    if (packGrams == null || packGrams <= 0) {
        useMessageStore().addMessage(MessageType.WARNING, {title: foodRef.name, text: t('BarcodeNoGrams')}, 4000)
        resetToScan()
        return
    }
    const api = new ApiApi()
    let food: Food | FoodSimple = foodRef
    try {
        food = await api.apiFoodRetrieve({id: foodRef.id})
    } catch {
        // FoodSimple is enough to create an entry
    }
    const sle = {
        amount: 1,
        amountGrams: packGrams,
        food: food,
        shoppingLists: useShoppingStore().shoppingLists.filter(sl => sl.id != null && useUserPreferenceStore().deviceSettings.shopping_selected_shopping_lists.includes(sl.id)),
    } as ShoppingListEntry
    await useShoppingStore().createObject(sle, true)
    useMessageStore().addMessage(MessageType.SUCCESS, {title: food.name, text: t('Added_To_Shopping_List')}, 2000)
    resetToScan()
}

async function confirmAssociate() {
    if (!canAssociate.value || !pendingUpc.value) {
        return
    }
    saving.value = true
    const api = new ApiApi()
    try {
        const created = await api.apiFoodBarcodeCreate({
            foodBarcode: {
                upc: pendingUpc.value,
                brand: associateBrand.value || null,
                qty: associateQty.value,
                unitId: associateUnit.value!.id,
                foodId: associateFood.value!.id,
            },
        })
        await applyKnownFood(created)
    } catch (err) {
        useMessageStore().addError(ErrorMessageType.CREATE_ERROR, err)
    } finally {
        saving.value = false
    }
}
</script>
