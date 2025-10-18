# Merak Trip Planner Web Client

Phase 2 of the frontend roadmap bootstraps a React 19 + Next.js 15 application that will host the chat
experience for the Merak agent. The project is colocated with the Python backend but deploys as an
independent Node.js service.

## Prerequisites

- Node.js 24.5 or newer (see `.nvmrc` in the repo root or use Volta)
- `npm`, `pnpm`, or `yarn` for dependency management (examples assume `npm`)

## Available Scripts

```bash
npm install          # install dependencies
npm run dev          # start the dev server on http://localhost:3000
npm run lint         # run ESLint with Next.js core web vital rules
npm run test         # execute Vitest (jsdom environment)
npm run typecheck    # verify TypeScript configuration
npm run build        # create a production build
npm run start        # serve the production build
```

## Architecture Notes

- The App Router (`app/`) is enabled with React 19 Server Components.
- ESLint uses the new flat config format with `next/core-web-vitals` and Prettier interop.
- Vitest provides fast component testing; the initial configuration loads `@testing-library/jest-dom`.
- Experimental React Compiler is enabled to align with React 19 guidance from the [Next.js 15 docs](https://github.com/vercel/next.js/blob/v15.1.8/docs/01-app/03-api-reference/05-config/01-next-config-js/reactCompiler.mdx).

The chat workflow and API proxy will be added in Phase 4 once the backend streaming pipeline is in place.
