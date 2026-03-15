import time

import pytest

from app.mobile_backend import ApiError, MobileBackend, RateLimitPolicy


def create_backend(rate_limit: int = 120) -> MobileBackend:
    return MobileBackend(
        jwt_secret="test-secret",
        rate_limit_policy=RateLimitPolicy(requests_per_minute=rate_limit),
    )


def test_auth_and_device_registration_flow():
    backend = create_backend()
    user = backend.register_user("alice@example.com", "password123")
    token = backend.login("alice@example.com", "password123")["access_token"]
    user_id = backend.authenticate(token)

    assert user_id == user["user_id"]

    reg = backend.register_device(user_id, "dev-ios-1", "ios", "apns-token-1")
    assert reg["registered"] is True


def test_idempotency_key_returns_same_response_for_duplicate_submit():
    backend = create_backend()
    user_id = backend.register_user("bob@example.com", "pw")["user_id"]

    first = backend.upsert_item(
        user_id=user_id,
        item_id="task-1",
        payload={"title": "Buy milk", "done": False},
        idempotency_key="idem-1",
    )
    duplicate = backend.upsert_item(
        user_id=user_id,
        item_id="task-1",
        payload={"title": "Buy milk", "done": True},
        idempotency_key="idem-1",
    )

    assert duplicate == first
    assert duplicate["version"] == 1


def test_sync_cursor_and_etag_flow():
    backend = create_backend()
    user_id = backend.register_user("sync@example.com", "pw")["user_id"]

    backend.upsert_item(user_id, "item-1", {"v": 1}, idempotency_key="k1")
    backend.upsert_item(user_id, "item-2", {"v": 2}, idempotency_key="k2")

    first_sync = backend.sync(user_id=user_id, cursor=0)
    assert len(first_sync["changes"]) == 2

    second_sync = backend.sync(user_id=user_id, cursor=first_sync["next_cursor"], etag=first_sync["etag"])
    assert second_sync["not_modified"] is True
    assert second_sync["changes"] == []


def test_conflict_requires_merge_then_retry():
    backend = create_backend()
    user_id = backend.register_user("conflict@example.com", "pw")["user_id"]

    created = backend.upsert_item(user_id, "item-c", {"v": 1}, idempotency_key="k3")

    with pytest.raises(ApiError) as exc:
        backend.upsert_item(
            user_id,
            "item-c",
            {"v": 2},
            idempotency_key="k4",
            expected_version=created["version"] + 1,
        )

    assert exc.value.code == "SYNC_CONFLICT"
    assert exc.value.status == 409


def test_push_pipeline_and_duplicate_notification_protection():
    backend = create_backend()
    user_id = backend.register_user("push@example.com", "pw")["user_id"]
    backend.register_device(user_id, "dev-a1", "android", "fcm-token-a1")

    result = backend.send_push(user_id, "Hi", "body", notification_id="n1")
    duplicate = backend.send_push(user_id, "Hi", "body", notification_id="n1")

    assert result["status"] == "queued"
    assert duplicate["status"] == "duplicate_ignored"
    assert len(backend.events()) == 1


def test_rate_limit_with_retry_behavior_edge_case():
    backend = create_backend(rate_limit=2)
    user_id = backend.register_user("ratelimit@example.com", "pw")["user_id"]

    backend.sync(user_id)
    backend.sync(user_id)

    with pytest.raises(ApiError) as exc:
        backend.sync(user_id)

    assert exc.value.status == 429
    assert exc.value.details["retry_after_seconds"] == 60


def test_network_retry_simulation_duplicate_delivery():
    backend = create_backend()
    user_id = backend.register_user("retry@example.com", "pw")["user_id"]

    req = dict(user_id=user_id, item_id="retry-item", payload={"count": 1}, idempotency_key="network-1")
    first = backend.upsert_item(**req)

    # Simulate client timeout then retry with same idempotency key.
    time.sleep(0.01)
    second = backend.upsert_item(**req)

    assert first == second
    assert backend.sync(user_id)["changes"][0]["version"] == 1
