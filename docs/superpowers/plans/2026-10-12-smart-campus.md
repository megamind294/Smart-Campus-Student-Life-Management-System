# Smart Campus Implementation Plan
> Execution: implement inline in the fresh empty repository requested by the user.
Goal: deliver a runnable student dashboard matching the project proposal with JSON data.
Architecture: Vite React TypeScript app, typed data model, Context state, localStorage, separate pages, common UI components.
Tech stack: React, TypeScript, React Router, Tailwind CSS, Lucide icons, Vitest, Testing Library.
Spec: docs/superpowers/specs/2026-10-12-smart-campus.md
Global constraints: JSON dummy data; no backend; six supplied team members; browser-only edits; SPA responsive navigation.
Review focus: malformed stored data, midnight/date boundaries, empty grades/sessions, keyboard task movement, mobile overflow.
## Tasks
- [x] 1. Set up Vite/TypeScript and data model; write failing tests for summary, attendance, task validation and storage recovery; implement helpers and typed seed data.
- [x] 2. Write failing UI tests for task creation, movement, persistence and module navigation; implement shell, shared state, forms and six pages.
- [x] 3. Add responsive styles, README, Kanban process documentation and CI; run full tests and build; inspect desktop/mobile screenshots; push reviewed source through GitHub.
Commands: npm test (all tests pass), npm run build (TypeScript and Vite succeed).

## Verification record
- Model and UI suite: 19 tests passing.
- Production build: TypeScript and Vite successful.
- Independent review: fixed course accordion keyboard focus and inert mobile navigation; aligned due-this-week count to the calendar week.
- Browser screenshots: unavailable because Chromium download was blocked/truncated by this environment; desktop/mobile visual inspection remains for the team.
