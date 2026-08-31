#!/usr/bin/env bash
# Seed vue3/node_modules with Linux-native packages for this container.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VUE="${ROOT}/vue3"

echo "==> Preparing Vue dependencies for this container OS..."

if [[ ! -f "${VUE}/package.json" ]]; then
    echo "ERROR: ${VUE}/package.json is missing. Is the workspace mounted?" >&2
    exit 1
fi

mkdir -p "${VUE}/node_modules"

if [[ ! -e "${VUE}/node_modules/vite/package.json" && -d /opt/vue3-deps/node_modules ]]; then
    echo "==> Seeding node_modules from the Linux image..."
    cp -a /opt/vue3-deps/node_modules/. "${VUE}/node_modules/"
fi

cd "${VUE}"
yarn install

if ! node --input-type=module -e "await import('vite')" >/dev/null 2>&1; then
    echo "==> Vite could not load (likely host OS bindings). Reinstalling..."
    rm -rf node_modules
    yarn install
    if ! node --input-type=module -e "await import('vite')" >/dev/null 2>&1; then
        echo "ERROR: Vue native bindings are still missing after a clean install." >&2
        exit 1
    fi
fi

echo "==> Vue dependencies are ready."
echo "==> Start the app with: ./start.sh"
