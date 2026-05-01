# Frontend — Ledger

React + TypeScript + Vite. Talks to the FastAPI backend at `localhost:8000`.


```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

Open <http://localhost:5173>.

In dev, `VITE_USE_MOCK_API=true` is the default, the app runs against a
seeded in-memory dataset so you can build and demo without depending on the
backend's CRUD endpoints (which are still stubs that return 501). Use
`demo / demo` at the login screen for the seed data.

To talk to the real backend set `VITE_USE_MOCK_API=false` in `.env`.
Make sure `docker compose up --build` is running at the repo root first.

## Architecture

```
src/
├── api/         # API clients — one chokepoint per resource
│   ├── client.ts        Fetch wrapper, handles auth & error parsing
│   ├── mock.ts          In-memory backend (toggled by env var)
│   ├── auth.ts, accounts.ts, transactions.ts, balance.ts
├── auth/        # Auth context — current user, login/logout
├── components/  # Reusable UI
│   └── layout/
├── lib/         # Pure utilities — currency, dates
├── pages/       # Top-level route components
├── styles/      # Global CSS, design tokens
└── types/       # API types — mirror Pydantic models
```

### Auth, today vs. tomorrow

Currently every protected backend endpoint takes `?user_id=<uuid>` as a
query parameter (no real JWT yet). The API client attaches it automatically.

When `POST /token` ships, swap the auth attachment in `src/api/client.ts`
from query param to `Authorization: Bearer <token>` header 

### Why the mock layer

The backend's `DummyModel` raises `TodoError` on most CRUD operations, so
real endpoints return 501 today. The mock layer lets us build and demo the
full UI immediately. Schema is identical, so flipping `VITE_USE_MOCK_API`
is a one-line change once the backend's ready.

## Required deliverables (assignment scope)

-  Create transaction form — `src/pages/NewTransactionPage.tsx`
-  Transaction list — `src/pages/TransactionsPage.tsx`
-  Delete transaction button (with confirmation) — same page
-  Login / register
-  Dashboard with total balance and recent activity
-  Account management (create, list, close)

## Build for production

```bash
npm run build
npm run preview   # smoke-test the build
```

Output goes to `dist/`. For deployment we'd serve via nginx or include in
docker-compose as a third service.
