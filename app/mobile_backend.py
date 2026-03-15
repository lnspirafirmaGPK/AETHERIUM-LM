from __future__ import annotations

import base64
import hashlib
import hmac
import json
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Tuple


class ApiError(Exception):
    def __init__(self, code: str, message: str, status: int, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.code = code
        self.message = message
        self.status = status
        self.details = details or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "error": {
                "code": self.code,
                "message": self.message,
                "details": self.details,
            }
        }


@dataclass
class RetryPolicy:
    timeout_ms: int = 5000
    max_retries: int = 3
    base_backoff_ms: int = 200
    jitter_ratio: float = 0.2
    retryable_statuses: Tuple[int, ...] = (408, 425, 429, 500, 502, 503, 504)


@dataclass
class RateLimitPolicy:
    requests_per_minute: int = 120


@dataclass
class SyncRecord:
    item_id: str
    user_id: str
    payload: Dict[str, Any]
    version: int
    updated_at: datetime
    deleted: bool = False


@dataclass
class DeviceRegistration:
    user_id: str
    device_id: str
    platform: str
    push_token: str
    updated_at: datetime


@dataclass
class IdempotentResponse:
    status: int
    body: Dict[str, Any]


@dataclass
class MobileBackend:
    jwt_secret: str
    retry_policy: RetryPolicy = field(default_factory=RetryPolicy)
    rate_limit_policy: RateLimitPolicy = field(default_factory=RateLimitPolicy)
    token_ttl_minutes: int = 60
    _users: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    _device_regs: Dict[str, DeviceRegistration] = field(default_factory=dict)
    _sync_records: Dict[str, SyncRecord] = field(default_factory=dict)
    _idempotency: Dict[Tuple[str, str], IdempotentResponse] = field(default_factory=dict)
    _request_windows: Dict[str, List[float]] = field(default_factory=dict)
    _events: List[Dict[str, Any]] = field(default_factory=list)
    _cursor: int = 0

    def register_user(self, email: str, password: str) -> Dict[str, Any]:
        if email in self._users:
            raise ApiError("AUTH_CONFLICT", "Email already exists", 409)
        salt = uuid.uuid4().hex
        digest = hashlib.sha256(f"{salt}:{password}".encode()).hexdigest()
        user = {"id": uuid.uuid4().hex, "email": email, "password_hash": digest, "salt": salt}
        self._users[email] = user
        return {"user_id": user["id"], "email": email}

    def login(self, email: str, password: str) -> Dict[str, Any]:
        user = self._users.get(email)
        if not user:
            raise ApiError("AUTH_INVALID", "Invalid credentials", 401)
        digest = hashlib.sha256(f"{user['salt']}:{password}".encode()).hexdigest()
        if not hmac.compare_digest(digest, user["password_hash"]):
            raise ApiError("AUTH_INVALID", "Invalid credentials", 401)
        token = self._issue_jwt(user["id"])
        return {"access_token": token, "token_type": "Bearer", "expires_in": self.token_ttl_minutes * 60}

    def authenticate(self, token: str) -> str:
        try:
            header_b64, payload_b64, signature = token.split(".")
            signed = f"{header_b64}.{payload_b64}".encode()
            expected = hmac.new(self.jwt_secret.encode(), signed, hashlib.sha256).hexdigest()
            if not hmac.compare_digest(signature, expected):
                raise ApiError("AUTH_INVALID_TOKEN", "Invalid token signature", 401)
            payload = json.loads(base64.urlsafe_b64decode(payload_b64.encode() + b"=="))
            if payload["exp"] < int(time.time()):
                raise ApiError("AUTH_EXPIRED", "Token expired", 401)
            return payload["sub"]
        except ApiError:
            raise
        except Exception as exc:
            raise ApiError("AUTH_INVALID_TOKEN", "Malformed token", 401, {"reason": str(exc)}) from exc

    def register_device(self, user_id: str, device_id: str, platform: str, push_token: str) -> Dict[str, Any]:
        if platform not in {"ios", "android"}:
            raise ApiError("VALIDATION_ERROR", "Unsupported platform", 400)
        self._device_regs[device_id] = DeviceRegistration(
            user_id=user_id,
            device_id=device_id,
            platform=platform,
            push_token=push_token,
            updated_at=datetime.now(timezone.utc),
        )
        return {"device_id": device_id, "platform": platform, "registered": True}

    def upsert_item(
        self,
        user_id: str,
        item_id: str,
        payload: Dict[str, Any],
        idempotency_key: str,
        expected_version: Optional[int] = None,
    ) -> Dict[str, Any]:
        self._enforce_rate_limit(user_id)
        idem_key = (user_id, idempotency_key)
        if idem_key in self._idempotency:
            return self._idempotency[idem_key].body

        current = self._sync_records.get(item_id)
        if current and current.user_id != user_id:
            raise ApiError("FORBIDDEN", "Item owned by another user", 403)

        if current and expected_version is not None and current.version != expected_version:
            raise ApiError(
                "SYNC_CONFLICT",
                "Version mismatch",
                409,
                {"server_version": current.version, "conflict_strategy": "client_merge_then_retry"},
            )

        next_version = (current.version + 1) if current else 1
        now = datetime.now(timezone.utc)
        record = SyncRecord(
            item_id=item_id,
            user_id=user_id,
            payload=payload,
            version=next_version,
            updated_at=now,
            deleted=False,
        )
        self._sync_records[item_id] = record
        self._cursor += 1

        body = {
            "item_id": item_id,
            "version": next_version,
            "cursor": self._cursor,
            "etag": self._etag(record),
            "updated_at": now.isoformat(),
        }
        self._idempotency[idem_key] = IdempotentResponse(status=200, body=body)
        return body

    def sync(self, user_id: str, cursor: int = 0, etag: Optional[str] = None, limit: int = 50) -> Dict[str, Any]:
        self._enforce_rate_limit(user_id)
        changes: List[Dict[str, Any]] = []
        for rec in sorted(self._sync_records.values(), key=lambda r: r.version):
            if rec.user_id != user_id:
                continue
            if rec.version <= cursor:
                continue
            item = {
                "item_id": rec.item_id,
                "version": rec.version,
                "payload": rec.payload,
                "deleted": rec.deleted,
                "etag": self._etag(rec),
                "updated_at": rec.updated_at.isoformat(),
            }
            changes.append(item)
            if len(changes) >= limit:
                break

        current_etag = hashlib.sha256(json.dumps(changes, sort_keys=True).encode()).hexdigest()
        if not changes and etag:
            return {"changes": [], "next_cursor": cursor, "etag": etag, "not_modified": True}
        if etag and etag == current_etag:
            return {"changes": [], "next_cursor": cursor, "etag": current_etag, "not_modified": True}

        next_cursor = max([cursor] + [item["version"] for item in changes])
        return {"changes": changes, "next_cursor": next_cursor, "etag": current_etag, "not_modified": False}

    def send_push(self, user_id: str, title: str, body: str, notification_id: str) -> Dict[str, Any]:
        dedupe_key = f"{user_id}:{notification_id}"
        for event in self._events:
            if event["dedupe_key"] == dedupe_key:
                return {"notification_id": notification_id, "status": "duplicate_ignored"}

        devices = [d for d in self._device_regs.values() if d.user_id == user_id]
        if not devices:
            raise ApiError("PUSH_NO_DEVICE", "No registered device", 404)

        for device in devices:
            provider = "APNs" if device.platform == "ios" else "FCM"
            self._events.append(
                {
                    "dedupe_key": dedupe_key,
                    "provider": provider,
                    "device_id": device.device_id,
                    "push_token": device.push_token,
                    "title": title,
                    "body": body,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                }
            )

        return {
            "notification_id": notification_id,
            "status": "queued",
            "targets": [d.device_id for d in devices],
        }

    def events(self) -> List[Dict[str, Any]]:
        return list(self._events)

    def _enforce_rate_limit(self, user_id: str) -> None:
        now = time.time()
        window_start = now - 60
        requests = self._request_windows.setdefault(user_id, [])
        self._request_windows[user_id] = [x for x in requests if x >= window_start]
        self._request_windows[user_id].append(now)

        if len(self._request_windows[user_id]) > self.rate_limit_policy.requests_per_minute:
            raise ApiError(
                "RATE_LIMITED",
                "Too many requests",
                429,
                {
                    "limit_per_minute": self.rate_limit_policy.requests_per_minute,
                    "retry_after_seconds": 60,
                },
            )

    def _issue_jwt(self, user_id: str) -> str:
        header = {"alg": "HS256", "typ": "JWT"}
        payload = {"sub": user_id, "exp": int((datetime.now(timezone.utc) + timedelta(minutes=self.token_ttl_minutes)).timestamp())}
        header_b64 = base64.urlsafe_b64encode(json.dumps(header).encode()).decode().rstrip("=")
        payload_b64 = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip("=")
        signed = f"{header_b64}.{payload_b64}".encode()
        signature = hmac.new(self.jwt_secret.encode(), signed, hashlib.sha256).hexdigest()
        return f"{header_b64}.{payload_b64}.{signature}"

    @staticmethod
    def _etag(rec: SyncRecord) -> str:
        body = json.dumps({"item_id": rec.item_id, "version": rec.version, "payload": rec.payload}, sort_keys=True)
        return hashlib.sha256(body.encode()).hexdigest()
