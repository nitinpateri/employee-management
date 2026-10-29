# Employee Management (Flask + Supabase)

Simple CRUD app for employees. Flask frontend, Supabase Postgres backend (via the REST API), deployable on Vercel.

## Run locally

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in values, then export them
flask --app app run
```

## Environment variables

- `SUPABASE_URL`
- `SUPABASE_KEY` (publishable key)
- `SECRET_KEY`

## Note

The demo RLS policies allow the anon key to read and write `employees`. Add authentication and tighten the policies before real use.
