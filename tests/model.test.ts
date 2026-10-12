import { describe, it, expect } from 'vitest';
import { attendancePercent, averageGrade, validateTask, summarize, loadState, seedState, startOfWeek } from '../src/lib/model';
describe('academic calculations',()=>{
 it('computes attendance across unequal class counts',()=>expect(attendancePercent([{attended:9,total:10},{attended:1,total:2}])).toBe(83));
 it('handles no attendance and no grades',()=>{expect(attendancePercent([])).toBe(0);expect(averageGrade([])).toBe(null)});
 it('uses an arithmetic grade mean',()=>expect(averageGrade([{value:3},{value:5}])).toBe(4));
});
describe('task input',()=>{
 it('rejects whitespace-only titles',()=>expect(validateTask({title:'  ',due:'2026-10-20',courseId:'web'})).toBe('Enter a task title.'));
 it('rejects invalid calendar dates',()=>expect(validateTask({title:'Report',due:'2026-02-30',courseId:'web'})).toBe('Choose a valid due date.'));
});
describe('workspace state',()=>{
 it('recovers malformed storage',()=>{localStorage.setItem('smart-campus-v1','oops');expect(loadState()).toEqual(seedState)});
 it('recovers structurally invalid storage',()=>{localStorage.setItem('smart-campus-v1',JSON.stringify({tasks:[{title:'bad'}]}));expect(loadState()).toEqual(seedState)});
 it('counts overdue unfinished tasks but excludes completed tasks',()=>{const s=summarize([{status:'todo',due:'2026-10-10'},{status:'done',due:'2026-10-10'},{status:'progress',due:'2026-10-20'}], '2026-10-12');expect(s).toEqual({pending:2,done:1,overdue:1,progress:33})});
});

it('starts a Sunday calendar week on the preceding Monday',()=>expect(startOfWeek('2026-10-18')).toBe('2026-10-12'));
