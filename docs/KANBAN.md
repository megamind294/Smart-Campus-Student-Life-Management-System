# Development Kanban

Use GitHub Projects or Trello to maintain the team's real development history. The app's task board manages sample academic tasks; it does not replace the development board.

## Columns

Backlog → To Do → In Progress → Review / Testing → Done.

Set a suggested WIP limit of one In Progress card per member. Each card needs an owner, short description and acceptance criteria. A blocked task should explain the blocker. Review board flow regularly and save genuine activity history for the assignment.

## Definition of Done

- Acceptance criteria met and no unresolved functional errors.
- Relevant tests and production build pass.
- Another team member reviews the change.
- Documentation updated when behavior changes.
- Feature works at mobile and desktop widths.

## Initial demo implementation

Foundation, JSON records, overview, courses, assignments, calendar, academic records and simulated group projects are implemented in the initial code. Do not mark review requirements complete until the team actually reviews them.

## Follow-up backlog

| Work item | Acceptance criteria |
| --- | --- |
| Team code review | Each member can explain their module and documents review feedback. |
| Accessibility review | Test keyboard navigation, screen readers and touch controls. |
| Backend design | Agree on authentication, per-student records and project access. |
| Shared project data | Authorized members see each other's updates via a backend. |
| File attachments | Add upload rules, storage limits and access control. |
| Automated browser tests | Cover task creation, calendar synchronization and reload persistence. |
| Demo presentation | Demonstrate features and the team's actual Kanban history. |
