from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.mobile_backend import MobileBackend


def main() -> None:
    backend = MobileBackend(jwt_secret="local-secret")
    user_id = backend.register_user("sim@example.com", "pw")["user_id"]

    first = backend.upsert_item(
        user_id=user_id,
        item_id="note-1",
        payload={"text": "hello", "version": 1},
        idempotency_key="idem-sim-1",
    )
    retry = backend.upsert_item(
        user_id=user_id,
        item_id="note-1",
        payload={"text": "hello-updated", "version": 2},
        idempotency_key="idem-sim-1",
    )

    print("first:", first)
    print("retry:", retry)
    print("same_response=", first == retry)


if __name__ == "__main__":
    main()
