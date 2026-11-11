# STATE

## Decisions

Sem novas decisões globais. ADRs 001–015 existentes continuam vigentes; escolhas do diagnóstico M0 são locais à feature.

## Handoff

- **Feature**: m0-foundation
- **Phase / Task**: Phase3 concluída / T19 próxima; quatro lotes sequenciais autorizados
- **Completed**: T1–T12 c7dab16; T13 e7545d8; T14 ff6e718; T15 69d7f7d; T16 dcb59f2; T17 9b2bf47; T18 neste commit
- **Gates**:232 Pytest,3 Vitest,1 Chromium probe passed; locked uv, Ruff/format, typecheck/build, spec/tasks validators green
- **In-progress**: nenhum; batch3 concluído
- **Next step**: batch4 T19–T22: OpenAPI/TS generation, actual Web/bootstrap/launcher, real crash/restart harness, operational commands/acceptance
- **Blockers**: nenhum. Actual UI/static serving/health/docs routes/API runtime launcher not yet delivered. Desktop browser unvalidated. Only .serena/ preexisting outside scope
- **Branch**: main

Interfaces: `resume_api.app.create_app(service=DiagnosticService(repo), runtime_root=Path, environment="development", origin="http://127.0.0.1:8000", reconciler=optional)` returns FastAPI; no database migration or Redis creation. It exposes POST /api/session/bootstrap, POST /api/diagnostics (202new/200same key, DiagnosticResponse envelope), GET /api/diagnostics/latest. HTTPX TestClient base_url must match canonical origin. Protected routes enforce exactHost/Origin/session before streaming<=1024-byte body. POST requires Origin+JSON. Every response has no-store/no-referrer/self-only CSP/X-Request-ID(serverUUID); errors sanitized. `BootstrapRequest/Response` Pydantic exist. T19 should explicitly describe actual sanitized error models in OpenAPI (default validation schema is not actual error payload), add health minimal and protected docs/schema. No manual TS DTOs.

Session: `SessionChannel(runtime_root,environment,store=SessionStore())` context; validates private runtime root and ancestors, creates `resume-builder/<environment>/`0700, api.lock0600/flock, bootstrap.sock0600 with SO_PEERCRED. Socket sends JSON ticket on connect, no client request required. Ticket256bit/30s/one-use; memory-only session cookie `resume_session`HttpOnly/SameSiteStrict/Path/, no expiry. close invalidates all sessions/tickets. Launcher T20 must validate socket path/owner and get ticket without printing it, open fragment URL; clear fragment before fetch. Real Chromium probe exists but definitive app browser flow remains T20.

Delivery: `resume_core.broker.make_broker(redis_url, namespace)` enforces127.0.0.1 RedisURL and namespace, socket/connect timeouts0.2s, redis retries0; no startup of server. `RedisPublisher(broker).publish(execution)` sends Message `diagnostics/run_diagnostic`, args canonical id/requestId only, max_retries0. `DiagnosticReconciler(repo,publisher).tick()` offloads SQLite/network to threads, reserves per-second delivery atomically (`repo.reserve_delivery()`), conditional `repo.finish_delivery(id,bool)` never regresses running/terminal. `.run(asyncio.Event stop)` fixed1s tick. API lifespan runs tick before yield, stops loop/channel on shutdown.

Worker: `process_diagnostic(repo,id,request_id,fixture=run_fixture)` validates canonical correlation before claim, pure fixed fixture, lease/token guarded complete/fail; invalid/duplicate returnsFalse. `create_actor(repo,broker)` actor max_retries0/time_limit30000(supplement). Operator entrypoint `.venv/bin/python -m resume_worker --database /absolute/diagnostics.sqlite3 --redis-url redis://127.0.0.1:6379/0 --namespace resume-builder-development`; one process/thread, JSON logsstderr, stdoutempty, SIGTERM graceful, startup failure sanitized. No implicit migrations. API production CLI/justfile remains T22; uvicorn should use loopback, proxy_headers=False/log_config=None so safe logging is preserved.

Real Redis harness: `tests/integration/redis_harness.py` DockerRedis explicitly starts only its disposable test container, fixed127.0.0.1 ephemeralport across stop/start, tmpfs/no persistence, cleanup ownID. Pinned image downloaded by approved command: `redis@sha256:71885d8cc6e42f2bc0aa2eb853bfc4be200b5108a46ac50e117ae1df0531fb80`. No redis-server binary installed, Docker daemon accessible outside sandbox. `isolated_redis` and `redis_broker` fixtures in integration/conftest; namespaceunique per test. T17 actual outage/restart/queue-loss passed. T18 actual separate Worker/subprocess result+duplicates passed. T21 needs explicit real kill/restart during controlled processing, only test harness fault injection.

Commands: `.venv/bin/pytest tests/unit tests/integration tests/smoke -q --basetemp=/tmp/rb-b3` (short temp path necessary for Linux AF_UNIX108-byte path limit; real sockets/Docker require escalation). `.venv/bin/ruff check backend tests tools`; `.venv/bin/ruff format --check backend tests tools`; `uv sync --all-packages --locked`. `pnpm --filter web test`, typecheck, build. Chromium: `PLAYWRIGHT_BROWSERS_PATH=/tmp/resume-builder-playwright node apps/web/node_modules/@playwright/test/cli.js test --config apps/web/playwright.probe.config.ts`. T18 full232 Pytest passed; installed Starlette warns HTTPXTestClient deprecated towardHTTPX2(no new dependency added), browser color warning retained. .serena/ preexisting untracked; all feature changes committed. No private data/provider/CI/MCP used.
