import { describe, expect, it } from 'vitest';
import { renderToStaticMarkup } from 'react-dom/server';
import { Button } from '../src/shared/ui/button';
import { Input } from '../src/shared/ui/input';

describe('M1 UI primitives', () => {
  it('defaults a button to a safe non-submit type and forwards its label', () => {
    const html = renderToStaticMarkup(<Button>Open</Button>);
    expect(html).toContain('type="button"');
    expect(html).toContain('Open');
  });
  it('forwards input identifiers and native attributes', () => {
    const html = renderToStaticMarkup(<Input id="example" name="example" required />);
    expect(html).toContain('id="example"');
    expect(html).toContain('name="example"');
    expect(html).toContain('required');
  });
});
