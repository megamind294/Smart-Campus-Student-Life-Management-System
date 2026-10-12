import {useState,type FormEvent} from 'react';
import {Modal} from './ui';
import {courses,members,today,validateTask,type Task} from '../lib/model';
import {useWorkspace} from '../lib/workspace';
export function TaskEditor({task,onClose,projectId=''}:{task?:Task;onClose:()=>void;projectId?:string}){
 const {state,setState}=useWorkspace();const [error,setError]=useState('');
 const [draft,setDraft]=useState<Task>(task||{id:crypto.randomUUID(),title:'',description:'',courseId:projectId?state.projects.find(p=>p.id===projectId)?.courseId||courses[0].id:courses[0].id,status:'todo',priority:'medium',assigneeId:members[0].id,due:today(),projectId});
 const field=(name:keyof Task,value:string)=>setDraft(d=>({...d,[name]:value}));
 function submit(e:FormEvent){e.preventDefault();const message=validateTask(draft);if(message){setError(message);return}const value={...draft,title:draft.title.trim()};setState(s=>({...s,tasks:task?s.tasks.map(t=>t.id===task.id?value:t):[...s.tasks,value]}));onClose()}
 return <Modal title={task?'Edit task':'Create a task'} onClose={onClose}><form onSubmit={submit}>
 <label>Task title<input value={draft.title} onChange={e=>field('title',e.target.value)} maxLength={140} placeholder="What needs to be done?" required/></label>
 <label>Description<textarea value={draft.description} onChange={e=>field('description',e.target.value)} rows={3} placeholder="Notes, requirements or acceptance criteria"/></label>
 <div className="form-grid"><label>Course<select value={draft.courseId} onChange={e=>field('courseId',e.target.value)}>{courses.map(c=><option key={c.id} value={c.id}>{c.name}</option>)}</select></label><label>Due date<input type="date" value={draft.due} onChange={e=>field('due',e.target.value)} required/></label>
 <label>Priority<select value={draft.priority} onChange={e=>field('priority',e.target.value)}><option value="low">Low</option><option value="medium">Medium</option><option value="high">High</option></select></label><label>Assignee<select value={draft.assigneeId} onChange={e=>field('assigneeId',e.target.value)}>{members.map(m=><option key={m.id} value={m.id}>{m.name}</option>)}</select></label>
 <label>Status<select value={draft.status} onChange={e=>field('status',e.target.value)}><option value="todo">To Do</option><option value="progress">In Progress</option><option value="done">Completed</option></select></label><label>Project<select value={draft.projectId} onChange={e=>field('projectId',e.target.value)}><option value="">Independent assignment</option>{state.projects.map(p=><option key={p.id} value={p.id}>{p.name}</option>)}</select></label></div>
 {error&&<p role="alert" className="error">{error}</p>}<div className="form-actions"><button type="button" className="button secondary" onClick={onClose}>Cancel</button><button className="button" type="submit">Save task</button></div></form></Modal>
}
