# apps/api — MixSight FastAPI backend

Python 3.11+, FastAPI, sqlmodel/SQLAlchemy 2.0 async, Pydantic v2. Deps managed via `uv` per ADR-004. See root `CLAUDE.md` and `apps/api/CLAUDE.md` for conventions.

## First-time setup

```sh
cd apps/api
uv sync
cp ../../.env.example ../../.env
# edit DATABASE_URL etc. in the root .env
```

## Run the dev server

From repo root:
```sh
make up         # postgres + redis
make api        # FastAPI on :8000
```

Or directly:
```sh
cd apps/api
uv run uvicorn mixsight.main:app --reload --port 8000
```

`/healthz` returns 200 only when Postgres responds to `SELECT 1`.

## Tests

```sh
make test
# or
uv run pytest
```

From Week 1 Day 4-5 onward, tests enforce the §7.19 tenancy harness — authenticated endpoint tests missing the cross-tenant case fail the suite (see `@pytest.mark.tenancy_isolated`).
