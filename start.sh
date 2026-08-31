#!/usr/bin/env bash
# Start Stillroom development services: Vite first, then Django.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VUE="${ROOT}/vue3"
VITE_PORT="${VITE_PORT:-5173}"
DJANGO_PORT="${DJANGO_PORT:-8000}"
VITE_PID=""
DJANGO_PID=""

info() { echo "==> $*"; }
warn() { echo "WARNING: $*" >&2; }
die() { echo "ERROR: $*" >&2; exit 1; }

cleanup() {
    local exit_code=$?
    trap - EXIT INT TERM
    if [[ -n "${DJANGO_PID}" ]] && kill -0 "${DJANGO_PID}" 2>/dev/null; then
        info "Stopping Django (pid ${DJANGO_PID})..."
        kill "${DJANGO_PID}" 2>/dev/null || true
        wait "${DJANGO_PID}" 2>/dev/null || true
    fi
    if [[ -n "${VITE_PID}" ]] && kill -0 "${VITE_PID}" 2>/dev/null; then
        info "Stopping Vite (pid ${VITE_PID})..."
        kill "${VITE_PID}" 2>/dev/null || true
        wait "${VITE_PID}" 2>/dev/null || true
    fi
    exit "${exit_code}"
}

port_open() {
    local port="$1"
    python3 -c "import socket; s=socket.socket(); s.settimeout(0.3); s.connect(('127.0.0.1', ${port})); s.close()" 2>/dev/null
}

wait_for_port() {
    local port="$1"
    local name="$2"
    local attempts="${3:-90}"
    local i
    for ((i = 1; i <= attempts; i++)); do
        if port_open "${port}"; then
            return 0
        fi
        sleep 0.5
    done
    die "${name} did not become ready on port ${port} after $((attempts / 2))s."
}

vite_import_ok() {
    (cd "${VUE}" && node --input-type=module -e "await import('vite')") >/dev/null 2>&1
}

ensure_frontend_deps() {
    info "Checking Vue dependencies..."
    if [[ ! -f "${VUE}/package.json" ]]; then
        die "vue3/package.json is missing. Run this script from the Stillroom repo."
    fi

    if [[ ! -d "${VUE}/node_modules/vite" && -d /opt/vue3-deps/node_modules ]]; then
        info "Seeding Linux Vue dependencies from the image..."
        mkdir -p "${VUE}/node_modules"
        cp -a /opt/vue3-deps/node_modules/. "${VUE}/node_modules/"
    fi

    if ! vite_import_ok; then
        info "Installing Vue packages for this OS (native bindings). This can take a minute..."
        (cd "${VUE}" && yarn install) || die "yarn install failed in vue3/."
        if ! vite_import_ok; then
            warn "Vite still cannot load. Removing vue3/node_modules and retrying..."
            rm -rf "${VUE}/node_modules"
            (cd "${VUE}" && yarn install) || die "yarn install failed in vue3/."
            vite_import_ok || die "Vue native bindings are missing. Check node/yarn and vue3/yarn.lock."
        fi
    fi
    info "Vue dependencies are ready."
}

run_migrations() {
    info "Applying Django migrations..."
    if ! (cd "${ROOT}" && DEBUG=1 python3 manage.py migrate); then
        die "Django migrations failed. Check the output above."
    fi
}

start_vite() {
    if port_open "${VITE_PORT}"; then
        info "Vite is already running on port ${VITE_PORT}."
        return 0
    fi

    info "Starting Vite on port ${VITE_PORT}..."
    (
        cd "${VUE}"
        exec yarn dev
    ) &
    VITE_PID=$!

    if ! kill -0 "${VITE_PID}" 2>/dev/null; then
        die "Vite failed to start. Try: cd vue3 && yarn install && yarn dev"
    fi

    wait_for_port "${VITE_PORT}" "Vite"
    info "Vite is ready at http://localhost:${VITE_PORT}/static/vue3/"
}

start_django() {
    if port_open "${DJANGO_PORT}"; then
        info "Django is already running on port ${DJANGO_PORT}."
        return 0
    fi

    info "Starting Django on port ${DJANGO_PORT}..."
    (
        cd "${ROOT}"
        exec env DEBUG=1 python3 manage.py runserver "0.0.0.0:${DJANGO_PORT}"
    ) &
    DJANGO_PID=$!

    if ! kill -0 "${DJANGO_PID}" 2>/dev/null; then
        die "Django failed to start. Check Python dependencies and manage.py."
    fi

    wait_for_port "${DJANGO_PORT}" "Django"
    info "Django is ready at http://localhost:${DJANGO_PORT}/"
}

main() {
    cd "${ROOT}"
    info "Stillroom development services"
    info "Workspace: ${ROOT}"

    command -v python3 >/dev/null || die "python3 is not on PATH."
    command -v yarn >/dev/null || die "yarn is not on PATH. Rebuild the Dev Container."
    command -v node >/dev/null || die "node is not on PATH. Rebuild the Dev Container."
    [[ -f "${ROOT}/manage.py" ]] || die "manage.py not found in ${ROOT}."

    ensure_frontend_deps
    trap cleanup EXIT INT TERM
    start_vite
    run_migrations
    start_django

    echo
    info "Open http://localhost:${DJANGO_PORT}/ to test."
    info "Vite HMR: http://localhost:${VITE_PORT}/  (must be up before Django)"
    echo

    if [[ -z "${VITE_PID}" && -z "${DJANGO_PID}" ]]; then
        info "Both services were already running. Nothing to supervise."
        return 0
    fi

    info "Watching services. Press Ctrl+C to stop processes started by this script."

    while true; do
        if [[ -n "${VITE_PID}" ]] && ! kill -0 "${VITE_PID}" 2>/dev/null; then
            die "Vite exited unexpectedly (pid ${VITE_PID})."
        fi
        if [[ -n "${DJANGO_PID}" ]] && ! kill -0 "${DJANGO_PID}" 2>/dev/null; then
            die "Django exited unexpectedly (pid ${DJANGO_PID})."
        fi
        if [[ -z "${VITE_PID}" || -z "${DJANGO_PID}" ]]; then
            # One service was pre-existing; wait on the one we started.
            if [[ -n "${VITE_PID}" ]]; then
                wait "${VITE_PID}" || die "Vite exited unexpectedly (pid ${VITE_PID})."
            fi
            if [[ -n "${DJANGO_PID}" ]]; then
                wait "${DJANGO_PID}" || die "Django exited unexpectedly (pid ${DJANGO_PID})."
            fi
            break
        fi
        sleep 2
    done
}

main "$@"
