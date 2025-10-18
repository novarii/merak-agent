# Merak Web Frontend

The Next.js application that powers the Merak Trip Planner web experience now lives in
`frontend/merak_web`. Phase 2 of the implementation plan bootstraps the project with React 19, the App
Router, and repo-aligned tooling.

## Tech Stack
- Node.js ≥24.5 runtime (see `.nvmrc` inside the project for a suggested version)
- Next.js 15 + React 19 (App Router + Server Components)
- TypeScript strict mode
- ESLint (flat config) + Prettier formatting
- Vitest + Testing Library for component tests (jsdom environment)

## Getting Started
```bash
cd frontend/merak_web
npm install
npm run dev
```

Additional scripts mirror the Python tooling conventions:

- `npm run lint` — checks with `next lint` using `next/core-web-vitals`
- `npm run test` — runs Vitest with jsdom + Testing Library
- `npm run typecheck` — validates the TypeScript project
- `npm run build` / `npm run start` — production build + runtime

Refer to `.agent/Tasks/frontend_next_plan.md` for the full roadmap. Phase 3 will layer in shared UI
components and the ChatKit proxy route once backend streaming integration is stable.
