import type { ComponentProps } from 'react';
import * as Primitive from '@radix-ui/react-dialog';

// Composition adapted from shadcn/ui's Radix Dialog; behavior comes from Radix.
export const Dialog = Primitive.Root;
export const DialogTrigger = Primitive.Trigger;
export const DialogClose = Primitive.Close;
export const DialogTitle = Primitive.Title;
export const DialogDescription = Primitive.Description;
export function DialogContent({ className = '', children, ...props }: ComponentProps<typeof Primitive.Content>) {
  return <Primitive.Portal><Primitive.Overlay className="fixed inset-0 bg-slate-900/50" /><Primitive.Content className={`fixed left-1/2 top-1/2 w-80 -translate-x-1/2 -translate-y-1/2 rounded-lg bg-white p-6 text-slate-900 shadow-lg ${className}`} {...props}>{children}</Primitive.Content></Primitive.Portal>;
}
