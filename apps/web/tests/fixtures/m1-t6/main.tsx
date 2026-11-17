import { createRoot } from 'react-dom/client';
import { useState } from 'react';
import { Button } from '../../../src/shared/ui/button';
import { Input } from '../../../src/shared/ui/input';
import { Dialog, DialogTrigger, DialogContent, DialogTitle, DialogDescription, DialogClose } from '../../../src/shared/ui/dialog';
import '../../../src/shared/tailwind.css';

function Fixture() {
  const [value, setValue] = useState('');
  return <main><Dialog><DialogTrigger asChild><Button>Open dialog</Button></DialogTrigger><DialogContent><DialogTitle>Example form</DialogTitle><DialogDescription>Fictional test values only.</DialogDescription><form onSubmit={(event) => { event.preventDefault(); setValue(new FormData(event.currentTarget).get('name')?.toString() ?? ''); }}><label htmlFor="name">Name</label><Input id="name" name="name" /><Button type="submit">Save</Button></form><output aria-label="Saved value">{value}</output><DialogClose asChild><Button>Close</Button></DialogClose></DialogContent></Dialog></main>;
}
createRoot(document.getElementById('root')!).render(<Fixture />);
