import type { ComponentProps } from 'react';

// Minimal project-owned adaptation of shadcn/ui's Button pattern.
export function Button({ className = '', type = 'button', ...props }: ComponentProps<'button'>) {
  return <button data-slot="button" type={type} className={`inline-flex items-center justify-center rounded-md bg-slate-900 px-4 py-2 text-white focus-visible:outline-2 focus-visible:outline-offset-2 ${className}`} {...props} />;
}
