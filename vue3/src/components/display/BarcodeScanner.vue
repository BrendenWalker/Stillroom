<template>
    <div>
        <div :id="readerId" class="barcode-scanner-preview mb-3"></div>
        <v-alert v-if="cameraError" type="warning" density="compact" class="mb-3">
            {{ $t('BarcodeCameraUnavailable') }}
        </v-alert>
        <v-text-field
            ref="upcField"
            v-model="manualUpc"
            :label="$t('Barcode')"
            autocomplete="off"
            autofocus
            hide-details
            @keydown.enter.prevent="submitManual"
        >
            <template #append>
                <v-btn icon="fa-solid fa-barcode" color="create" @click="submitManual"></v-btn>
            </template>
        </v-text-field>
    </div>
</template>

<script setup lang="ts">
import {nextTick, onBeforeUnmount, onMounted, ref} from "vue";
import {Html5Qrcode, Html5QrcodeSupportedFormats} from "html5-qrcode";

const emit = defineEmits<{ scanned: [code: string] }>()

const readerId = `barcode-reader-${Math.random().toString(36).slice(2, 10)}`
const manualUpc = ref('')
const cameraError = ref(false)
const upcField = ref<{ focus: () => void } | null>(null)

let scanner: Html5Qrcode | null = null
let running = false

onMounted(async () => {
    await nextTick()
    upcField.value?.focus()
    await startCamera()
})

onBeforeUnmount(() => {
    stopCamera()
})

async function startCamera() {
    try {
        scanner = new Html5Qrcode(readerId, {
            verbose: false,
            formatsToSupport: [
                Html5QrcodeSupportedFormats.EAN_13,
                Html5QrcodeSupportedFormats.EAN_8,
                Html5QrcodeSupportedFormats.UPC_A,
                Html5QrcodeSupportedFormats.UPC_E,
            ],
        })
        await scanner.start(
            {facingMode: 'environment'},
            {
                fps: 8,
                qrbox: {width: 280, height: 140},
            },
            (decodedText: string) => {
                emitScanned(decodedText)
            },
            () => undefined,
        )
        running = true
    } catch {
        cameraError.value = true
        running = false
    }
}

async function stopCamera() {
    if (!scanner || !running) {
        return
    }
    try {
        await scanner.stop()
        scanner.clear()
    } catch {
        // camera already stopped
    }
    running = false
}

function emitScanned(code: string) {
    const trimmed = code.trim()
    if (!trimmed) {
        return
    }
    emit('scanned', trimmed)
}

function submitManual() {
    emitScanned(manualUpc.value)
    manualUpc.value = ''
}

defineExpose({focus: () => upcField.value?.focus()})
</script>

<style scoped>
.barcode-scanner-preview {
    min-height: 180px;
    overflow: hidden;
    border-radius: 8px;
    background: #111;
}

.barcode-scanner-preview :deep(video) {
    width: 100%;
}
</style>
