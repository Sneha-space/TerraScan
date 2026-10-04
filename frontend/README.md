# BhoomiNetra frontend

The officer's console: upload scanned khatians, see what the machine read, and check and
verify the records it wasn't sure about.

React 18 + Vite + Tailwind 3. Icons from `lucide-react`. The Anek fonts (Latin, Bengali,
Devanagari) ship inside the app, so they load without internet access.

## Run it

```bash
npm install
npm run dev
```

Open http://localhost:5173. The backend must be running at the address in `.env`
(`VITE_API_BASE_URL`, default `http://127.0.0.1:8000`) — copy `.env.example` to `.env`
to change it.

For something to look at, seed the backend with test data — see
`backend/scratch/seed_dev_data.py`.

## Screens

| Path | Screen |
|---|---|
| `/` | Overview: where records stand, machine accuracy, districts, oldest waiting |
| `/review` | Review queue: records that need an officer, and why |
| `/records` | Every record, filterable by status or by file (`?document=ID`) |
| `/uploads` | Upload a file; every file and what happened to it |
| `/records/:id` | Review one record beside its scan, correct either language, verify |

## Where things live

```
src/
  api/          client.js (axios, error messages), endpoints.js (one function per route)
  hooks/        useApi.js — loading / error / data for one API call
  components/
    layout/     AppShell (sidebar, phone menu), PageHeader
    common/     Button, StatusStamp, SearchField, loading / error / empty states
    records/    RecordTable, Bilingual (value as written + English)
    review/     LedgerRow (one field), ScanViewer
    overview/   the overview panels
    uploads/    FileDropzone
  pages/        one file per screen
  utils/        fields.js (labels, groups), format.js, script.js (which Indian script)
```

The API routes and their shapes are in `docs/frontend-api-guide.md`.

## Design

Colours come from land-record paperwork and are defined once in `tailwind.config.js`:
register ink (`ink`), paper (`paper`), the red ink officers correct with (`correction` —
also used for "needs review"), a seal green (`seal` — verified), and `machine` blue for
records the machine approved. Never use a raw hex colour in a component; add a token.
