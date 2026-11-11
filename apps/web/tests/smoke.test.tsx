import { describe, expect, it } from 'vitest';
import { renderToStaticMarkup } from 'react-dom/server';
import { App } from '../src/App';

describe('M0 workspace smoke (FND-20/21)', () => {
  it('renders the application identity', () => {
    expect(renderToStaticMarkup(<App />)).toContain('<h1>Resume Builder</h1>');
  });
  it('instructs the user to open an authorized local session', () => {
    expect(renderToStaticMarkup(<App />)).toContain('Abra pelo comando local para iniciar uma sessão autorizada.');
  });
  it('does not expose unfinished diagnostic actions', () => {
    expect(renderToStaticMarkup(<App />)).not.toContain('<button');
  });
});
