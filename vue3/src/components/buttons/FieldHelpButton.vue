<template>
    <v-menu location="end" :close-on-content-click="false">
        <template #activator="{ props: menuProps }">
            <v-btn
                v-bind="menuProps"
                icon="fa-solid fa-question"
                size="small"
                variant="text"
                density="compact"
                :aria-label="$t('Help')"
            ></v-btn>
        </template>
        <v-card max-width="320" class="pa-3 text-body-2">
            {{ text }}
        </v-card>
    </v-menu>
</template>

<script setup lang="ts">

defineProps({
    text: {type: String, required: true},
})

</script>
