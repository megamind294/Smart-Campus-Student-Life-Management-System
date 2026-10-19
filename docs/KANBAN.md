# Part II — Requirements, MVP, and Kanban

## Product requirements

Smart Campus is a responsive single-page student workspace. It brings common academic information and activities into one place so students can check their progress and manage their study week.

### Core functionalities

| Functionality | User need |
| --- | --- |
| Overview | See upcoming work, today's classes, course progress, grades, and attendance at a glance. |
| Courses | Review course details, instructors, credits, study materials, and related assignments. |
| Assignments | Create, edit, delete, filter, and update the status and priority of academic tasks. |
| Calendar | Review a weekly schedule and manage events; assignment deadlines stay in sync. |
| Grades and attendance | Record grades and attendance and see the resulting average and attendance rate. |
| Group projects | Organize local project tasks and see project completion and team members. |

The current product is a front-end demo. It uses sample academic data and browser `localStorage`; it does not provide accounts, a backend, or shared real-time data.

## MVP (first version)

The MVP focuses on the individual student's essential weekly workflow:

- A responsive overview with upcoming assignments and today's classes.
- A course list with course details and study materials.
- Assignment creation, editing, deletion, filtering, priorities, and status updates.
- A weekly calendar with event management and assignment deadlines.
- Grade and attendance recording with summary calculations.
- Persistence in the current browser, with clear demo/sample-data limitations.

Group projects are present as a local simulation, but shared project collaboration, accounts, and a server are not MVP requirements. They remain future work. The MVP does not claim to connect to university systems or store official academic records.

## GitHub Kanban board

The team development board is [Smart Campus - Part II Kanban](https://github.com/users/megamind294/projects/2), with the [Part II Board view](https://github.com/users/megamind294/projects/2/views/1). It is separate from the academic assignment board inside the app. Keep the board's three workflow columns:

1. **To Do** — agreed work that has not started.
2. **In Progress** — work currently being done.
3. **Done** — work whose acceptance criteria have been met.

Create one issue or card per task. Include a short description, acceptance criteria, and an actual team owner. Move cards as work happens; do not backdate or invent progress. Keep the number of active cards realistic, and explain blockers in the issue. Use GitHub's activity history as evidence of the team's actual process.

### Definition of Done

- The task's acceptance criteria are met with no known functional errors.
- Relevant tests and the production build pass.
- A team member reviews the work.
- Related documentation is updated.
- The feature works at mobile and desktop widths.

## Current implementation and follow-up work

The initial code already implements the overview, courses, assignments, calendar, academic records, and simulated group projects. Their existence in the code is not evidence that the team completed a Kanban process or reviewed them. Record only genuine task ownership, progress, and review in the GitHub board.

| Follow-up work | Acceptance criteria |
| --- | --- |
| Team code review | Each member can explain their module and documents review feedback. |
| Accessibility review | Test keyboard navigation, screen readers, and touch controls; record findings. |
| Backend design | Agree on authentication, per-student records, and project access before implementation. |
| Shared project data | Authorized members can see each other's updates through an agreed backend. |
| File attachments | Define upload rules, storage limits, and access control. |
| Automated browser tests | Cover task creation, calendar synchronization, and reload persistence. |
| Demo presentation | Demonstrate product functionality and the team's genuine GitHub Kanban history. |
