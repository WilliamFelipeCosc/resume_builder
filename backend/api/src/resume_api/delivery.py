"""Durable diagnostic delivery/recovery. Broker calls run outside SQLite transactions."""

import asyncio

import structlog


class DiagnosticReconciler:
    def __init__(self, repository, publisher):
        self.repository, self.publisher = repository, publisher
        self._lock = asyncio.Lock()

    async def tick(self):
        async with self._lock:
            await asyncio.to_thread(self.repository.reconcile)
            due = await asyncio.to_thread(self.repository.reserve_delivery)
            if due is None:
                return
            try:
                await asyncio.to_thread(self.publisher.publish, due)
            except Exception:
                await asyncio.to_thread(self.repository.finish_delivery, due.id, False)
                structlog.get_logger().warning(
                    "delivery_failed",
                    execution_id=due.id,
                    request_id=due.request_id,
                    code="queue_unavailable",
                )
            else:
                await asyncio.to_thread(self.repository.finish_delivery, due.id, True)
                structlog.get_logger().info(
                    "diagnostic_queued", execution_id=due.id, request_id=due.request_id
                )

    async def run(self, stop):
        loop = asyncio.get_running_loop()
        next_tick = loop.time() + 1
        while not stop.is_set():
            try:
                await asyncio.wait_for(stop.wait(), timeout=max(0, next_tick - loop.time()))
                return
            except TimeoutError:
                pass
            try:
                await self.tick()
            except Exception:
                structlog.get_logger().error("internal_error", code="internal_error")
            next_tick += 1
            if next_tick < loop.time():
                next_tick = loop.time()
