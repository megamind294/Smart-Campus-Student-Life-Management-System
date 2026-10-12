# Smart Campus — Student Life Management System

A responsive React + TypeScript single-page application for the WSB Agile Project Management group project. Courses, assignments, a weekly timetable, grades, attendance and group projects live in one student workspace.

## Run locally

Requires Node.js 22.12+ (Node 24 recommended) and npm.

```bash
npm ci
npm run dev
```

Open the local URL printed by Vite. If your environment restricts network interfaces, use `npm run dev -- --host 127.0.0.1`.

```bash
npm test        # model and UI integration tests
npm run build  # TypeScript check + production build
npm run preview
```

## Features

- **Overview:** derived task counts, deadlines, today's classes, course progress, grade mean and attendance.
- **Courses:** sample instructors, ECTS credits, expandable study materials and related assignments.
- **Assignments:** create, edit, delete and filter tasks; drag between Kanban columns or use a keyboard-accessible status selector; priorities and owners.
- **Calendar:** navigate seven-day weeks, add/edit/delete events; assignment deadlines follow task dates automatically.
- **Grades & attendance:** record/delete grades, update course attendance; arithmetic grade mean and session-weighted attendance.
- **Group projects:** create local projects, assign tasks, track completion and view the six-person team.
- Search within the current page; mobile navigation; reset demo confirmation; local persistence.

## Data and limitations

`src/data/campus.json` contains JSON seed records. Academic records, instructors, events and assignments are illustrative. The team names and IDs were supplied for this project. Seed deadline offsets are converted to actual dates when the app first loads, so a new demo stays relevant. Existing saved dates are preserved across reloads.

Changes are saved to `localStorage` under `smart-campus-v1`. If storage is corrupt, sample data is restored; if browser storage is unavailable, a notice explains that edits are session-only. Reset demo data restores the seed state. Reset does not affect another browser.

There is **no backend, login, university API or real-time collaboration**. Project ownership is a local simulation. Refresh-safe hash routing works on static hosts. The build is in `dist/`; serve it using `npm run preview` or a static web host (not by double-clicking index.html). Hosting configuration may require Vite's `base` option for a subdirectory.

Grades range from 2 to 5. The displayed average is an arithmetic mean, not an official weighted university GPA. Attendance equals attended sessions / recorded sessions across courses. Courses without records contribute no sessions.

## Project structure

```text
src/
  data/campus.json          # seed data and team members
  lib/model.ts             # types, dates, validation and calculations
  lib/workspace.tsx        # shared state and localStorage
  components/              # reusable UI and task form
  pages/                   # six feature modules
  App.tsx                  # shell and navigation
  styles.css               # responsive design + Tailwind import
```

## Team

| Member | Student ID |
| --- | --- |
| Rinkle Sharma | 67784 |
| Sai Sri Akkireddi | 66918 |
| Elienne Rugwiro | 72066 |
| Zakaria Elbarmaki | 70562 |
| Mohammed-elamine Kobbi | 67964 |
| Favour Oluwagbemiga | 64494 |

## Kanban development

See [docs/KANBAN.md](docs/KANBAN.md) for workflow, work-in-progress rules and a suggested backlog. The academic task board inside the app is distinct from the team's development board. Documentation is a suggested process, not evidence that meetings or reviews happened.
