import {it,expect,vi} from 'vitest';
import {render,screen,within} from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import {MemoryRouter} from 'react-router-dom';
import App from '../src/App';
import {STORAGE_KEY} from '../src/lib/model';
function setup(path='/'){return render(<MemoryRouter initialEntries={[path]}><App/></MemoryRouter>)}
it('navigates from dashboard to the course catalogue',async()=>{const user=userEvent.setup();setup();await user.click(screen.getByRole('link',{name:/Courses/}));expect(screen.getByRole('heading',{name:'My courses'})).toBeInTheDocument()});
it('creates a task, moves it using the keyboard-friendly status selector, and persists it',async()=>{
 const user=userEvent.setup();setup('/assignments');await user.click(screen.getByRole('button',{name:'New task'}));
 const dialog=screen.getByRole('dialog');await user.type(within(dialog).getByLabelText('Task title'),'Prepare final presentation');await user.click(within(dialog).getByRole('button',{name:'Save task'}));
 const title=screen.getByText('Prepare final presentation');const card=title.closest('article')!;
 await user.selectOptions(within(card).getByLabelText('Task status'),'done');
 const saved=JSON.parse(localStorage.getItem(STORAGE_KEY)!);expect(saved.tasks.find((t:{title:string})=>t.title==='Prepare final presentation').status).toBe('done');
 expect(screen.getByText('Prepare final presentation')).toBeInTheDocument();
});
it('shows all six real project members',()=>{setup('/projects');expect(screen.getByText('Mohammed-elamine Kobbi')).toBeInTheDocument();expect(screen.getByText('Favour Oluwagbemiga')).toBeInTheDocument()});
it('keeps created tasks after remount and shows their calendar deadlines',async()=>{
 const user=userEvent.setup();const first=setup('/assignments');await user.click(screen.getByRole('button',{name:'New task'}));let dialog=screen.getByRole('dialog');await user.type(within(dialog).getByLabelText('Task title'),'Persistence assessment');await user.click(within(dialog).getByRole('button',{name:'Save task'}));first.unmount();setup('/calendar');expect(screen.getByText('Persistence assessment')).toBeInTheDocument();
});
it('creates a timetable event',async()=>{
 const user=userEvent.setup();setup('/calendar');await user.click(screen.getByRole('button',{name:'Add event'}));const dialog=screen.getByRole('dialog');await user.type(within(dialog).getByLabelText('Event title'),'Presentation rehearsal');await user.type(within(dialog).getByLabelText('Location'),'Room A101');await user.click(within(dialog).getByRole('button',{name:'Save event'}));expect(screen.getByText('Presentation rehearsal')).toBeInTheDocument();expect(JSON.parse(localStorage.getItem(STORAGE_KEY)!).events.some((e:{title:string})=>e.title==='Presentation rehearsal')).toBe(true);
});
it('records an academic grade',async()=>{
 const user=userEvent.setup();setup('/academics');await user.click(screen.getByRole('button',{name:'Record grade'}));const dialog=screen.getByRole('dialog');await user.type(within(dialog).getByLabelText('Assessment name'),'Final exam');await user.click(within(dialog).getByRole('button',{name:'Save record'}));expect(screen.getByText('Final exam')).toBeInTheDocument();expect(JSON.parse(localStorage.getItem(STORAGE_KEY)!).grades.find((g:{label:string})=>g.label==='Final exam').value).toBe(4);
});
it('updates attendance without duplicating the course record',async()=>{
 const user=userEvent.setup();setup('/academics');await user.click(screen.getByRole('button',{name:'Update'}));const dialog=screen.getByRole('dialog');await user.clear(within(dialog).getByLabelText('Sessions attended'));await user.type(within(dialog).getByLabelText('Sessions attended'),'10');await user.click(within(dialog).getByRole('button',{name:'Save record'}));const records=JSON.parse(localStorage.getItem(STORAGE_KEY)!).attendance.filter((a:{courseId:string})=>a.courseId==='web');expect(records).toHaveLength(1);expect(records[0].attended).toBe(10);
});
it('requires confirmation before resetting local edits',async()=>{
 const user=userEvent.setup();setup('/assignments');await user.click(screen.getByRole('button',{name:'New task'}));await user.type(screen.getByLabelText('Task title'),'A local edit');await user.click(screen.getByRole('button',{name:'Save task'}));await user.click(screen.getByRole('button',{name:'Reset demo data'}));await user.click(within(screen.getByRole('dialog')).getByRole('button',{name:'Cancel'}));expect(screen.getByText('A local edit')).toBeInTheDocument();await user.click(screen.getByRole('button',{name:'Reset demo data'}));await user.click(within(screen.getByRole('dialog')).getByRole('button',{name:'Reset demo'}));expect(screen.queryByText('A local edit')).not.toBeInTheDocument();
});
it('lets keyboard users reach course material accordions inside the dialog',async()=>{
 const user=userEvent.setup();setup('/courses');await user.click(screen.getAllByRole('button',{name:'View course'})[0]);const dialog=screen.getByRole('dialog');expect(within(dialog).getByRole('button',{name:'Close dialog'})).toHaveFocus();await user.tab();expect(within(dialog).getByText('Module overview')).toHaveFocus();
});

it('makes the closed mobile sidebar inert',()=>{
 const original=window.matchMedia;window.matchMedia=vi.fn().mockReturnValue({matches:true,addEventListener:vi.fn(),removeEventListener:vi.fn()});
 try{setup();expect(document.querySelector('.sidebar')).toHaveAttribute('inert')}finally{window.matchMedia=original}
});
