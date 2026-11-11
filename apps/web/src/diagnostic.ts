import { bootstrapSession, createDiagnostic, getLatestDiagnostic, type DiagnosticExecution } from '@resume-builder/api-client';

export function createApi(baseUrl: string, fetcher: typeof fetch = fetch) {
  const options = { baseUrl, fetch: fetcher, credentials: 'same-origin' as const };
  return {
    bootstrap: (ticket: string) => bootstrapSession({ ...options, body: { ticket } }),
    latest: () => getLatestDiagnostic(options),
    create: (idempotencyKey: string) => createDiagnostic({ ...options, body: { idempotencyKey } }),
  };
}
type Api = ReturnType<typeof createApi>;

export async function prepareSession(
  location: Pick<Location, 'hash' | 'pathname' | 'search'>,
  history: Pick<History, 'replaceState'>,
  api: Api,
): Promise<boolean> {
  const ticket = new URLSearchParams(location.hash.slice(1)).get('bootstrap');
  if (location.hash) history.replaceState(null, '', location.pathname + location.search);
  if (!ticket) return true;
  try { return (await api.bootstrap(ticket)).data?.authorized === true; }
  catch { return false; }
}

export type DiagnosticState = {
  authorized: boolean;
  submitting: boolean;
  execution: DiagnosticExecution | null;
  unavailable: boolean;
  uncertain: boolean;
};
export const initialState: DiagnosticState = {
  authorized: false, submitting: false, execution: null, unavailable: false, uncertain: false,
};
export const isActive = (execution: DiagnosticExecution | null) =>
  execution !== null && ['pending', 'queued', 'running'].includes(execution.status);

export class DiagnosticController {
  state: DiagnosticState = { ...initialState };
  private timer?: ReturnType<typeof setTimeout>;
  private stopped = false;
  private busy = false;
  private intentKey?: string;
  private listener: (state: DiagnosticState) => void = () => {};

  constructor(private api: Api, private uuid = () => crypto.randomUUID()) {}

  subscribe(listener: (state: DiagnosticState) => void) { this.listener = listener; }
  private update(patch: Partial<DiagnosticState>) {
    if (this.stopped) return;
    this.state = { ...this.state, ...patch };
    this.listener(this.state);
  }
  private unauthorized() {
    this.intentKey = undefined;
    this.update({ ...initialState });
    clearTimeout(this.timer);
  }
  private schedule() {
    clearTimeout(this.timer);
    if (!this.stopped && (this.state.unavailable || (this.state.authorized && (isActive(this.state.execution) || this.state.uncertain)))) {
      this.timer = setTimeout(() => { void this.refresh(); }, 1000);
    }
  }
  async start(sessionReady: Promise<boolean> = Promise.resolve(true)) {
    if (!(await sessionReady) || this.stopped) return;
    await this.refresh();
  }
  private accept(execution: DiagnosticExecution | null) {
    if (execution?.idempotencyKey === this.intentKey) this.intentKey = undefined;
    this.update({ authorized: true, execution, unavailable: false, uncertain: this.intentKey !== undefined });
  }
  async refresh() {
    if (this.stopped || this.busy) return;
    this.busy = true;
    try {
      const response = await this.api.latest();
      if (response.response?.status === 401) this.unauthorized();
      else if (response.data) this.accept(response.data.execution);
      else this.update({ unavailable: true });
    } catch { this.update({ unavailable: true }); }
    finally { this.busy = false; this.schedule(); }
  }
  async execute() {
    if (this.stopped || this.busy || !this.state.authorized || isActive(this.state.execution)) return;
    clearTimeout(this.timer);
    this.busy = true;
    this.intentKey ??= this.uuid();
    this.update({ submitting: true });
    let recover = false;
    try {
      const response = await this.api.create(this.intentKey);
      if (response.response?.status === 401) this.unauthorized();
      else if (response.data) this.accept(response.data.execution);
      else { this.update({ uncertain: true, unavailable: true }); recover = true; }
    } catch {
      this.update({ uncertain: true, unavailable: true });
      recover = true;
    } finally {
      this.busy = false;
      this.update({ submitting: false });
    }
    if (recover) await this.refresh();
    else this.schedule();
  }
  stop() { this.stopped = true; clearTimeout(this.timer); }
}
