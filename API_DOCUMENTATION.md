# 📦 HANA Auth Service Portal - API Documentation (Internal Test Version)

This document describes the external APIs available for integration with HAC.

## 🔐 Authentication
For the internal test phase, the API uses standard **Session Authentication** or **Basic Authentication**.

1. **Session Auth:** If calling from a browser where you are logged in, no extra headers are needed.
2. **Basic Auth:** For headless calls from HAC scripts:
   Include header: `Authorization: Basic <base64_encoded_username:password>`

---

## 🚀 Direct Deploy API (HAC Integration)
* **Endpoint:** `POST /du-automation/api/v1/direct-deploy/`
* **Purpose:** Headless deployment of the latest existing export.

### 📥 Request Body
```json
{
  "sid": "OAF",
  "du_name": "HANA_SIT_AM_TEN_RISE"
}
```

### 📤 Success Response (202 Accepted)
```json
{
  "message": "Direct Deployment initiated",
  "task_id": 142,
  "status_url": "/du-automation/api/v1/task-status/142/"
}
```

---

## 🔍 Task Status API
Check deployment progress.

* **Endpoint:** `GET /du-automation/api/v1/task-status/<task_id>/`

### 📤 Response Example
```json
{
  "status": "SUCCESS",
  "task_type": "IMPORT",
  "error_message": "System: OAF - Success: True - Output: Import complete..."
}
```
**Statuses:** `PENDING`, `RUNNING`, `SUCCESS`, `FAILURE`.
