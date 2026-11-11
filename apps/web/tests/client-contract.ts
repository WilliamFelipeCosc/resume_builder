// FND-20: compile a real frontend consumer of generated request, result and error types.
import { createDiagnostic, getLatestDiagnostic, type DiagnosticCreate, type DiagnosticExecution } from '@resume-builder/api-client';

export const request: DiagnosticCreate = { idempotencyKey: 'fixture-uuid-supplied-at-runtime' };

export async function consumeGeneratedContract() {
  const response = await createDiagnostic({ body: request });
  const execution: DiagnosticExecution | null | undefined = response.data?.execution;
  const code: string | undefined = response.error?.error.code;
  const latest = await getLatestDiagnostic();
  return { execution, code, latest: latest.data?.execution };
}

// @ts-expect-error Only the approved camelCase field belongs in the request.
export const invalid: DiagnosticCreate = { idempotency_key: 'invalid' };
