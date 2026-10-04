# Setup and run

Step by step, Windows PowerShell.

## 1. Backend packages (once)

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1        # mac/linux: source .venv/bin/activate
pip install -r requirements.txt
pip install torch --index-url https://download.pytorch.org/whl/cu124
```

Every later backend command assumes you are in `backend/` with the venv active.

## 2. LGD village list (once)

The government list of every village in India. Not in GitHub (too big), so download it yourself:

1. Download from https://dataful.in/datasets/21838/
2. Unzip it and take the big CSV inside
   (`list-of-states-districts-sub-districts-and-villages-along-with-their-lgd-codes-as-of-2-july-2026.csv`)
3. Rename it to `lgd_villages_2026-07-02.csv`
4. Put it in `backend/data/lgd/` (make the folders if missing)

## 3. Load the LGD list into the database (~5 seconds)

```powershell
python -m scripts.load_lgd
```

Run this again whenever you delete `backend/bhoominetra.db`: deleting the database wipes the LGD list too.

## 4. Start the backend

```powershell
uvicorn main:app --reload --reload-dir src
```

API docs: http://127.0.0.1:8000/docs

## 5. Start the frontend

In a second terminal. Needs Node.js.

```powershell
cd frontend
npm install        # first time only
npm run dev
```

Open http://localhost:5173
