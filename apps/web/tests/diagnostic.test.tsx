import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { renderToStaticMarkup } from 'react-dom/server';
import type { DiagnosticExecution } from '@resume-builder/api-client';
import { DiagnosticController, createApi, prepareSession } from '../src/diagnostic';
import { DiagnosticView } from '../src/App';

const KEY = 'c95643db-9cc5-4bc3-ac93-2738b3b6fb55';
const execution = (status: DiagnosticExecution['status'] = 'pending'): DiagnosticExecution => ({
  id: '536031fd-e4c2-46c5-a80c-b092c5565a9a', requestId: 'a2975a6e-5791-4008-bb3e-a4790df80036',
  idempotencyKey: KEY, status, attemptCount: status === 'pending' ? 0 : 1,
  createdAt: '2026-11-11T12:00:00Z', updatedAt: '2026-11-11T12:00:00Z',
  result: status === 'succeeded' ? { message: 'diagnostic_completed', fixtureVersion: 'm0-v1' } : null,
  error: status === 'failed' ? { code: 'deadline_exceeded', message: 'Diagnostic deadline exceeded.' } : null,
  deliveryWarning: null,
});
const response = (value: unknown, status = 200) => Response.json(value, { status });
const flush = async () => { for (let i = 0; i < 12; i++) await Promise.resolve(); };
const setup = (fetcher = vi.fn<typeof fetch>()) => {
  const controller = new DiagnosticController(createApi('http://127.0.0.1:8000', fetcher), () => KEY);
  return { controller, fetcher };
};

beforeEach(() => vi.useFakeTimers());
afterEach(() => vi.useRealTimers());

describe('FND-03/04/07/13/15 diagnostic UI', () => {
  it('recovers an initial connection failure without asking for new credentials', async () => {
    const { controller, fetcher } = setup();
    fetcher.mockRejectedValueOnce(new TypeError('offline')).mockResolvedValueOnce(response({ execution: null }));
    await controller.start();
    expect(controller.state.unavailable).toBe(true);
    await vi.advanceTimersByTimeAsync(1000);
    expect(controller.state.authorized).toBe(true);
    expect(controller.state.unavailable).toBe(false);
    controller.stop();
  });
  it('stops at401 and offers the local opening command', async () => {
    const { controller, fetcher } = setup();
    fetcher.mockResolvedValue(response({}, 401));
    await controller.start();
    expect(controller.state.authorized).toBe(false);
    expect(renderToStaticMarkup(<DiagnosticView state={controller.state} execute={() => {}} />)).toContain('Abra pelo comando local');
    await vi.advanceTimersByTimeAsync(5000);
    expect(fetcher).toHaveBeenCalledTimes(1);
  });

  it.each(['pending', 'queued', 'running'] as const)('restores %s with disabled action', async (status) => {
    const { controller, fetcher } = setup();
    fetcher.mockResolvedValue(response({ execution: execution(status) }));
    await controller.start();
    const html = renderToStaticMarkup(<DiagnosticView state={controller.state} execute={() => {}} />);
    expect(html).toContain('disabled=""');
    expect(html).toContain(execution().id);
    expect(controller.state.execution?.status).toBe(status);
    controller.stop();
  });

  it.each(['succeeded', 'failed'] as const)('shows persisted %s and enables new intention', async (status) => {
    const { controller, fetcher } = setup();
    fetcher.mockResolvedValue(response({ execution: execution(status) }));
    await controller.start();
    const html = renderToStaticMarkup(<DiagnosticView state={controller.state} execute={() => {}} />);
    expect(html).not.toContain('disabled=""');
    expect(html).toContain(status === 'succeeded' ? 'diagnostic_completed' : 'Diagnostic deadline exceeded.');
    await vi.advanceTimersByTimeAsync(5000);
    expect(fetcher).toHaveBeenCalledTimes(1);
  });

  it('cleans bootstrap fragment before any generated request', async () => {
    const fetcher = vi.fn<typeof fetch>().mockImplementation(async (request) => {
      expect(history.replaceState).toHaveBeenCalledWith(null, '', '/?view=diagnostic');
      expect((request as Request).url).not.toContain('PRIVATE_TICKET');
      expect(await (request as Request).json()).toEqual({ ticket: 'PRIVATE_TICKET' });
      return response({ authorized: true });
    });
    const history = { replaceState: vi.fn() };
    const ready = prepareSession({ hash: '#bootstrap=PRIVATE_TICKET', pathname: '/', search: '?view=diagnostic' }, history, createApi('http://127.0.0.1:8000', fetcher));
    expect(await ready).toBe(true);
    expect(fetcher).toHaveBeenCalledTimes(1);
  });

  it('failed bootstrap does not request diagnostic data', async () => {
    const { controller, fetcher } = setup();
    await controller.start(Promise.resolve(false));
    expect(controller.state.authorized).toBe(false);
    expect(fetcher).not.toHaveBeenCalled();
  });

  it('never overlaps polling while a previous request is unresolved', async () => {
    const { controller, fetcher } = setup();
    fetcher.mockResolvedValueOnce(response({ execution: execution() }));
    await controller.start();
    let resolve!: (value: Response) => void;
    fetcher.mockImplementationOnce(() => new Promise<Response>((done) => { resolve = done; }));
    await vi.advanceTimersByTimeAsync(1000);
    await vi.advanceTimersByTimeAsync(5000);
    expect(fetcher).toHaveBeenCalledTimes(2);
    resolve(response({ execution: execution('succeeded') }));
    await flush();
    expect(controller.state.execution?.status).toBe('succeeded');
    controller.stop();
  });

  it('keeps the intention key when an uncertainPOST must be retried', async () => {
    const { controller, fetcher } = setup();
    fetcher.mockResolvedValueOnce(response({ execution: null }));
    await controller.start();
    const keys: string[] = [];
    fetcher.mockImplementationOnce(async (request) => {
      keys.push((await (request as Request).json()).idempotencyKey);
      throw new TypeError('transport lost');
    }).mockResolvedValueOnce(response({ execution: null }));
    await controller.execute();
    expect(controller.state.uncertain).toBe(true);
    expect(controller.state.execution).toBeNull();
    fetcher.mockImplementationOnce(async (request) => {
      keys.push((await (request as Request).json()).idempotencyKey);
      return response({ execution: execution() }, 202);
    });
    await controller.execute();
    expect(keys).toEqual([KEY, KEY]);
    expect(controller.state.uncertain).toBe(false);
    expect(controller.state.execution?.id).toBe(execution().id);
    controller.stop();
  });

  it('does not send twice whilePOST is pending and disables the button', async () => {
    const { controller, fetcher } = setup();
    fetcher.mockResolvedValueOnce(response({ execution: null }));
    await controller.start();
    let resolve!: (value: Response) => void;
    fetcher.mockImplementationOnce(() => new Promise<Response>((done) => { resolve = done; }));
    const pending = controller.execute();
    await controller.execute();
    await flush(); // Let the generated SDK finish its asynchronous request preparation.
    expect(controller.state.submitting).toBe(true);
    expect(renderToStaticMarkup(<DiagnosticView state={controller.state} execute={() => {}} />)).toContain('disabled=""');
    expect(fetcher).toHaveBeenCalledTimes(2);
    resolve(response({ execution: execution() }, 202));
    await pending;
    controller.stop();
  });

  it('transport failure preserves the known active state without inventing failure', async () => {
    const { controller, fetcher } = setup();
    const run = { ...execution(), deliveryWarning: { code: 'queue_unavailable' as const, message: 'Queue is temporarily unavailable.' as const } };
    fetcher.mockResolvedValueOnce(response({ execution: run })).mockRejectedValueOnce(new TypeError('PRIVATE_NETWORK'));
    await controller.start();
    await vi.advanceTimersByTimeAsync(1000);
    expect(controller.state.execution).toEqual(run);
    const html = renderToStaticMarkup(<DiagnosticView state={controller.state} execute={() => {}} />);
    expect(html).toContain('Queue is temporarily unavailable.');
    expect(html).toContain('Conexão indisponível');
    expect(html).not.toContain('PRIVATE_NETWORK');
    controller.stop();
  });

  it('a polling401 clears diagnostics and stops further requests', async () => {
    const { controller, fetcher } = setup();
    fetcher.mockResolvedValueOnce(response({ execution: execution() })).mockResolvedValueOnce(response({}, 401));
    await controller.start();
    await vi.advanceTimersByTimeAsync(1000);
    expect(controller.state.authorized).toBe(false);
    expect(controller.state.execution).toBeNull();
    await vi.advanceTimersByTimeAsync(5000);
    expect(fetcher).toHaveBeenCalledTimes(2);
  });
});
