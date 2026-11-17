import './shared/tailwind.css';
import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { App } from './App';
import { createApi, prepareSession } from './diagnostic';

const root = createRoot(document.getElementById('root')!);
function openSession() {
  // Redeem once before StrictMode effect replay, including an already-open tab.
  const sessionReady = prepareSession(window.location, window.history, createApi(window.location.origin));
  root.render(<StrictMode><App sessionReady={sessionReady} /></StrictMode>);
}
openSession();
window.addEventListener('hashchange', openSession);
