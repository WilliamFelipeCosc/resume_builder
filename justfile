set shell := ["zsh", "-eu", "-c"]

default:
    @just --list

# Install only project dependencies; invoke explicitly.
setup:
    uv sync --all-packages --locked
    pnpm install --frozen-lockfile

# Redis lifecycle is a separate manual operator action.
redis-up:
    docker compose up --detach redis

redis-down:
    docker compose down

migrate:
    uv run --all-packages --locked python -m resume_api migrate

api:
    uv run --all-packages --locked python -m resume_api serve

worker:
    uv run --all-packages --locked python -m resume_api worker

open:
    uv run --all-packages --locked python -m resume_api open

# The MCP spike uses only the already installed environment.
mcp-spike-init:
    uv run --all-packages --locked --no-sync python -m resume_mcp_server init

mcp-spike-serve profile:
    uv run --all-packages --locked --no-sync python -m resume_mcp_server serve --profile {{quote(profile)}}

mcp-spike-form:
    uv run --all-packages --locked --no-sync python -m resume_mcp_server.form_server

mcp-spike-reports profile:
    uv run --all-packages --locked --no-sync python -m resume_mcp_server reports --profile {{quote(profile)}}

check-mcp-spike:
    uv run --all-packages --locked --no-sync pytest tests/unit/mcp_spike tests/integration/mcp_spike tests/smoke/test_mcp_spike_workspace.py tests/smoke/test_mcp_spike_commands.py -q --basetemp=/tmp/rb-m05-tests

build:
    pnpm --filter web build

generate:
    uv run --all-packages --locked python -m resume_api.export_openapi --output packages/api-client/openapi.json
    pnpm --filter @resume-builder/api-client generate

check-python:
    uv run --all-packages --locked pytest tests/unit tests/integration tests/smoke -q --basetemp=/tmp/rb-tests

check-web:
    pnpm --filter web test
    pnpm --filter web typecheck
    pnpm --filter web build

check-contract:
    uv run --all-packages --locked python -m tools.check_contract

check-browser:
    node apps/web/node_modules/@playwright/test/cli.js test --config apps/web/playwright.probe.config.ts
    node apps/web/node_modules/@playwright/test/cli.js test --config apps/web/playwright.app.config.ts

lint:
    uv run --all-packages --locked ruff check backend tests tools
    uv run --all-packages --locked ruff format --check backend tests tools
    git diff --check

check: check-python check-web check-contract check-browser lint
