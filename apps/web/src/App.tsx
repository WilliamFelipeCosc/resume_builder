import { useEffect, useState } from 'react';
import { createApi, DiagnosticController, initialState, isActive, type DiagnosticState } from './diagnostic';
import './style.css';

export function DiagnosticView({ state, execute }: { state: DiagnosticState; execute: () => void }) {
  const run = state.execution;
  return <main>
    <header><span className="eyebrow">FOUNDATION · M0</span><h1>Resume Builder</h1>
      <p>Diagnóstico local com dados de teste.</p></header>
    {!state.authorized ? <section>
      {state.unavailable && <p role="alert">Conexão indisponível. Tentando recuperar o estado.</p>}
      <p>Abra pelo comando local para iniciar uma sessão autorizada.</p><code>just open</code></section> :
      <section aria-label="Diagnóstico">
        <h2>Verificar o ambiente</h2>
        <p>Execute uma operação sintética e acompanhe seu resultado persistido.</p>
        <button onClick={execute} disabled={state.submitting || isActive(run)}>
          {state.submitting ? 'Enviando…' : state.uncertain ? 'Repetir envio' : 'Executar diagnóstico de teste'}
        </button>
        {state.unavailable && <p role="alert">Conexão indisponível. Tentando recuperar o estado.</p>}
        {state.uncertain && <p>O envio ainda não foi confirmado. Repetir usa a mesma intenção.</p>}
        {run ? <article aria-live="polite">
          <p role="status">{run.status}</p>
          <dl><dt>Execução</dt><dd><code data-testid="execution-id">{run.id}</code></dd>
            <dt>Tentativas</dt><dd>{run.attemptCount} / 3</dd></dl>
          {run.deliveryWarning && <p role="alert">{run.deliveryWarning.message}</p>}
          {run.result && <p>{run.result.message} · {run.result.fixtureVersion}</p>}
          {run.error && <p role="alert">{run.error.message}</p>}
        </article> : <p>Nenhum diagnóstico executado neste ambiente.</p>}
      </section>}
  </main>;
}

export function App({ sessionReady }: { sessionReady?: Promise<boolean> }) {
  const [state, setState] = useState<DiagnosticState>(initialState);
  const [controller, setController] = useState<DiagnosticController>();
  useEffect(() => {
    setState(initialState);
    const current = new DiagnosticController(createApi(window.location.origin));
    current.subscribe(setState);
    setController(current);
    void current.start(sessionReady);
    return () => current.stop();
  }, [sessionReady]);
  return <DiagnosticView state={state} execute={() => { void controller?.execute(); }} />;
}
