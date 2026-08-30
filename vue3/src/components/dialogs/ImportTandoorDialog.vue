<template>
    <v-card class="ml-auto mr-auto" max-width="300px" prepend-avatar="../../assets/logo_color.svg" :title="$t('ImportIntoTandoor')" @click="dialog = true">

    </v-card>

    <v-dialog max-width="800px" v-model="dialog">
        <v-card>
            <v-closable-card-title :title="$t('ImportIntoTandoor')" v-model="dialog"></v-closable-card-title>
            <v-card-text>
                <p>{{ $t('AboutTandoor') }}</p>
                <p>{{ $t('ImportIntoTandoorHelp') }}</p>

                <v-list-item border>
                    <v-card-title>1. {{ $t('URL') }}</v-card-title>
                    <v-text-field v-model="selfhostedUrl" :label="$t('Url')"></v-text-field>
                </v-list-item>
                <v-list-item border>
                    <v-card-title>2. {{ $t('Import') }}</v-card-title>
                    <template #append>
                        <v-btn icon="fa-solid fa-paper-plane" :href="selfhostedImportUrl" :disabled="selfhostedUrl == ''" target="_blank"></v-btn>
                    </template>
                </v-list-item>
            </v-card-text>
        </v-card>
    </v-dialog>
</template>


<script setup lang="ts">

import VClosableCardTitle from "@/components/dialogs/VClosableCardTitle.vue";
import {computed, ref} from "vue";

const selfhostedImportUrl = computed(() => {
    let selfhostedServerUrl = selfhostedUrl.value
    if (!selfhostedServerUrl.endsWith('/')) {
        selfhostedServerUrl += '/'
    }
    return selfhostedServerUrl + 'recipe/import/?url=' + location.href
})

const dialog = ref(false)
const selfhostedUrl = ref('')


</script>


<style scoped>

</style>
