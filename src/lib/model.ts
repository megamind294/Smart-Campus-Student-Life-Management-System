import data from '../data/campus.json';
export type Status='todo'|'progress'|'done';
export type Priority='low'|'medium'|'high';
export interface Task {id:string;title:string;description:string;courseId:string;status:Status;priority:Priority;assigneeId:string;due:string;projectId:string}
export interface CampusEvent {id:string;title:string;courseId:string;date:string;time:string;type:string;location:string}
export interface Grade {id:string;courseId:string;label:string;value:number}
export interface Attendance {courseId:string;attended:number;total:number}
export interface Project {id:string;name:string;description:string;courseId:string}
export interface State {version:1;tasks:Task[];events:CampusEvent[];grades:Grade[];attendance:Attendance[];projects:Project[]}
export const courses=data.courses;
export const members=data.members;
export const today=()=>dateKey(new Date());
export function dateKey(date:Date){return `${date.getFullYear()}-${String(date.getMonth()+1).padStart(2,'0')}-${String(date.getDate()).padStart(2,'0')}`}
export function addDays(date:string,days:number){const d=new Date(date+'T12:00:00');d.setDate(d.getDate()+days);return dateKey(d)}
export function validDate(date:string){if(!/^\d{4}-\d{2}-\d{2}$/.test(date))return false;const d=new Date(date+'T12:00:00');return !Number.isNaN(d.getTime()) && dateKey(d)===date}
export const prettyDate=(date:string)=>new Date(date+'T12:00:00').toLocaleDateString('en-GB',{day:'numeric',month:'short'});
export function startOfWeek(date:string){return addDays(date,-((new Date(date+'T12:00:00').getDay()+6)%7))}
const monday=()=>startOfWeek(today());
export const seedState:State={version:1,tasks:data.tasks.map(({dueOffset,...t})=>({...t,due:addDays(today(),dueOffset),status:t.status as Status,priority:t.priority as Priority})),events:data.events.map(({dayOffset,...e})=>({...e,date:addDays(monday(),dayOffset)})),grades:data.grades,attendance:data.attendance,projects:data.projects};
export const averageGrade=(grades:{value:number}[])=>grades.length ? Math.round(grades.reduce((n,g)=>n+g.value,0)/grades.length*100)/100:null;
export function attendancePercent(rows:{attended:number;total:number}[]){const total=rows.reduce((n,r)=>n+r.total,0);return total?Math.round(rows.reduce((n,r)=>n+r.attended,0)/total*100):0}
export function summarize(tasks:{status:string;due:string}[],date=today()){const done=tasks.filter(t=>t.status==='done').length;return {pending:tasks.length-done,done,overdue:tasks.filter(t=>t.status!=='done'&&t.due<date).length,progress:tasks.length?Math.round(done/tasks.length*100):0}}
export function validateTask(t:{title:string;due:string;courseId:string}){if(!t.title.trim())return 'Enter a task title.';if(!validDate(t.due))return 'Choose a valid due date.';if(!courses.some(c=>c.id===t.courseId))return 'Choose a course.';return ''}
export const STORAGE_KEY='smart-campus-v1';
export function loadState():State {
 try{
 const raw=localStorage.getItem(STORAGE_KEY);if(!raw)return structuredClone(seedState);
 const s=JSON.parse(raw) as State;
 const hasCourse=(id:string)=>courses.some(c=>c.id===id);
 if(s.version!==1 || !Array.isArray(s.tasks)||!Array.isArray(s.events)||!Array.isArray(s.grades)||!Array.isArray(s.attendance)||!Array.isArray(s.projects))throw Error('Bad state');
 if(!s.tasks.every(t=>typeof t.id==='string'&&typeof t.title==='string'&&typeof t.description==='string'&&typeof t.projectId==='string'&&typeof t.assigneeId==='string'&&hasCourse(t.courseId)&&validDate(t.due)&&['todo','progress','done'].includes(t.status)&&['low','medium','high'].includes(t.priority)))throw Error('Bad tasks');
 if(!s.events.every(e=>typeof e.id==='string'&&typeof e.title==='string'&&validDate(e.date)&&/^([01]\d|2[0-3]):[0-5]\d$/.test(e.time)&&hasCourse(e.courseId)&&typeof e.type==='string'&&typeof e.location==='string'))throw Error('Bad events');
 if(!s.grades.every(g=>typeof g.id==='string'&&hasCourse(g.courseId)&&typeof g.label==='string'&&Number.isFinite(g.value)&&g.value>=2&&g.value<=5))throw Error('Bad grades');
 if(!s.attendance.every(a=>hasCourse(a.courseId)&&Number.isInteger(a.total)&&Number.isInteger(a.attended)&&a.total>=0&&a.attended>=0&&a.attended<=a.total))throw Error('Bad attendance');
 if(!s.projects.every(p=>typeof p.id==='string'&&typeof p.name==='string'&&typeof p.description==='string'&&hasCourse(p.courseId)))throw Error('Bad projects');
 return s;
 }catch{return structuredClone(seedState)}
}
