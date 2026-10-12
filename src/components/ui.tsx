import {useEffect,useRef,type ReactNode} from 'react';
import {X,ArrowUpRight,BookOpen} from 'lucide-react';
import {courses,members,type Task} from '../lib/model';
export function PageHeading({eyebrow,title,description,action}:{eyebrow:string;title:string;description:string;action?:ReactNode}){return <div className="page-heading"><div><p className="eyebrow">{eyebrow}</p><h1>{title}</h1><p className="muted">{description}</p></div>{action}</div>}
export function Empty({message='No results. Try a different search.'}:{message?:string}){return <div className="empty"><BookOpen size={26}/><p>{message}</p></div>}
export function Badge({children,tone='sage'}:{children:ReactNode;tone?:string}){return <span className={`badge ${tone}`}>{children}</span>}
export function Progress({value}:{value:number}){return <div className="progress-track" role="progressbar" aria-label="Completion" aria-valuenow={value} aria-valuemin={0} aria-valuemax={100}><span style={{width:`${value}%`}}/></div>}
export function Avatar({id,size=''}:{id:string;size?:string}){const m=members.find(m=>m.id===id);return <span className={`avatar ${size}`} title={m?.name}>{m?.name.split(' ').slice(0,2).map(n=>n[0]).join('')||'?'}</span>}
export function CourseLabel({id}:{id:string}){const c=courses.find(c=>c.id===id);return <span className={`course-label ${c?.color}`}>{c?.code} <span>{c?.name}</span></span>}
export function Modal({title,children,onClose}:{title:string;children:ReactNode;onClose:()=>void}){
 const ref=useRef<HTMLDivElement>(null);
 useEffect(()=>{const prev=document.activeElement as HTMLElement;const el=ref.current;el?.querySelector<HTMLElement>('input,button,select,textarea')?.focus();const old=document.body.style.overflow;document.body.style.overflow='hidden';return ()=>{document.body.style.overflow=old;prev?.focus()}},[]);
 return <div className="modal-backdrop" onClick={e=>{if(e.target===e.currentTarget)onClose()}}><div ref={ref} className="modal" role="dialog" aria-modal="true" aria-label={title} onKeyDown={e=>{if(e.key==='Escape')onClose();if(e.key==='Tab'){const els=Array.from(ref.current?.querySelectorAll<HTMLElement>('button,input,select,textarea,a[href],summary')||[]).filter(el=>!el.hasAttribute('disabled'));const first=els[0],last=els[els.length-1];if(e.shiftKey&&document.activeElement===first){e.preventDefault();last?.focus()}else if(!e.shiftKey&&document.activeElement===last){e.preventDefault();first?.focus()}}}}><div className="modal-heading"><h2>{title}</h2><button className="icon-button" aria-label="Close dialog" onClick={onClose}><X size={20}/></button></div>{children}</div></div>
}
export function PanelTitle({title,children}:{title:string;children?:ReactNode}){return <div className="panel-heading"><h2>{title}</h2>{children||<ArrowUpRight size={18}/>}</div>}
export const matches=(value:string,query:string)=>value.toLowerCase().includes(query.toLowerCase().trim());
export function taskSearch(task:Task,query:string){return matches([task.title,task.description,courses.find(c=>c.id===task.courseId)?.name,members.find(m=>m.id===task.assigneeId)?.name].join(' '),query)}
