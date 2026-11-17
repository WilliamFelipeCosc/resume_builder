import type { ComponentProps } from 'react';

// Minimal project-owned adaptation of shadcn/ui's Input pattern.
export function Input({ className = '', ...props }: ComponentProps<'input'>) {
  return <input data-slot="input" className={`rounded-md border border-slate-300 px-3 py-2 focus-visible:outline-2 ${className}`} {...props} />;
}
