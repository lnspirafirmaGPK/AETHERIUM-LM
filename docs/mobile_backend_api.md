# Mobile Backend API Contract (iOS/Android)

## Goals
- JWT auth for mobile clients.
- Offline-friendly sync with `cursor`, `etag`, `version`.
- Idempotent write commands using `Idempotency-Key`.
- Push pipeline for APNs/FCM with duplicate protection.
- Retry/timeout and baseline rate-limit policy.

## Auth
### `POST /v1/auth/register`
Request
```json
{"email":"user@example.com","password":"string"}
```
Response `201`
```json
{"user_id":"uuid","email":"user@example.com"}
```

### `POST /v1/auth/login`
Response `200`
```json
{"access_token":"jwt","token_type":"Bearer","expires_in":3600}
```

## Device registration
### `POST /v1/devices`
Headers: `Authorization: Bearer <jwt>`
Request
```json
{"device_id":"string","platform":"ios|android","push_token":"string"}
```
Response `200`
```json
{"device_id":"string","platform":"ios","registered":true}
```

## Sync write (idempotent)
### `PUT /v1/sync/items/{item_id}`
Headers:
- `Authorization`
- `Idempotency-Key` (required for critical writes)
- `If-Match-Version` (optional optimistic lock)

Request
```json
{"payload":{"title":"Buy milk","done":false}}
```
Response `200`
```json
{"item_id":"task-1","version":2,"cursor":9,"etag":"sha256","updated_at":"ISO8601"}
```
Conflict `409`
```json
{"error":{"code":"SYNC_CONFLICT","message":"Version mismatch","details":{"server_version":2,"conflict_strategy":"client_merge_then_retry"}}}
```

## Sync read
### `GET /v1/sync?cursor=<int>&etag=<str>&limit=50`
Response `200`
```json
{"changes":[{"item_id":"task-1","version":2,"payload":{},"deleted":false,"etag":"...","updated_at":"..."}],"next_cursor":2,"etag":"hash","not_modified":false}
```
If same ETag:
```json
{"changes":[],"next_cursor":2,"etag":"hash","not_modified":true}
```

## Push notifications
### `POST /v1/push/send`
Request
```json
{"notification_id":"string","title":"Hi","body":"Hello"}
```
Response `200`
```json
{"notification_id":"string","status":"queued","targets":["device-id"]}
```
If duplicate notification_id per user:
```json
{"notification_id":"string","status":"duplicate_ignored"}
```

## Error model
```json
{"error":{"code":"RATE_LIMITED","message":"Too many requests","details":{"limit_per_minute":120,"retry_after_seconds":60}}}
```

## Reliability policies
- Timeout: 5s default request timeout.
- Retry: max 3 attempts, exponential backoff from 200ms + jitter.
- Retryable status: `408,425,429,500,502,503,504`.
- Rate limit baseline: `120 req/min/user`.

## Conflict strategy
- Use optimistic version checks (`If-Match-Version`).
- On `409 SYNC_CONFLICT`: client fetches latest (`GET /v1/sync`), merges local pending state, retries with new idempotency key.
