# AETHERIUM-LM

AETHERIUM-LM is a platform for experimenting with asynchronous LLM integration and reasoning workflows.

## Core components

- **Backend services (`app/`)** for system configuration, database access, and LLM helpers.
- **Reasoning engine (`cogitator_x/`)** for thought-path generation and evaluation with MCTS + Process Reward Model.

## Key structure

- `app/config.py` — database URL, global LLM configs, API keys.
- `app/db.py` — SQLAlchemy async models and session factory.
- `app/services/llm_service.py` — LLM config validation, embeddings, and role-based model selection.
- `app/services/platform_work.py` — platform workstream planning and initiative/backlog persistence.
- `cogitator_x/` — reasoning runtime.
- `tests/` — unit tests for reasoning and service logic.

## Quick start

1. Install dependencies

   ```bash
   pip install -r requirements.txt
   ```

2. Run tests

   ```bash
   pytest -q
   ```

## Platform update status

Previously missing capability has now been implemented:

- Structured platform planning package generation (workstreams, options, risks, rollout/rollback, production DoD).
- Database persistence for `Initiative -> Epic -> Story -> Task` entities.
- Redundant suggestion text has been removed; this README reflects the current single source of truth.

## Notes

- `GLOBAL_LLM_CONFIGS` in `app/config.py` are system defaults and use negative IDs to distinguish from DB records.
- Demo UI flow remains available in `main.py` (Flet).


## Mobile backend module

A production-oriented mobile backend reference implementation is included in `app/mobile_backend.py` with:

- JWT-based auth and device registration for iOS/Android push routing.
- Offline-friendly sync (`cursor`, `etag`, `version`) and optimistic conflict handling.
- Idempotent writes for duplicate/retry-safe commands.
- Baseline retry/timeout and user-level rate-limit enforcement.
- Push deduplication across APNs/FCM notification fanout.

See `docs/mobile_backend_api.md` for API contract and policies, and `scripts/simulate_duplicate_retry.py` for duplicate retry simulation.
