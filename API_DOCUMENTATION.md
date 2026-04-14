# 📦 HANA Auth Service Portal - API Documentation

This document describes the external APIs available for integration with HAC (HANA Administration Center).

## 🔐 Authentication
All API requests (except for obtaining tokens) require a JWT Bearer Token.

1. **Obtain Token:** 
   `POST /api/v1/token/`
   Body: `{"username": "...", "password": "..."}`
   Returns: `{"access": "...", "refresh": "..."}`

2. **Usage:**
   Include the header: `Authorization: Bearer <your_access_token>`

---

## 🚀 Direct Deploy API (HAC Integration)
Automatically finds the most recent export of a Delivery Unit (DU) and deploys it to a target system SID.

* **Endpoint:** `POST /api/v1/du-automation/direct-deploy/`
* **Purpose:** Headless deployment without triggering a new export.

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
  "filename_used": "HANA_SIT_AM_TEN_RISE_20240414.tgz",
  "status_url": "/api/v1/du-automation/task-status/142/"
}
```

### ❌ Error Responses
* `400 Bad Request`: Missing `sid` or `du_name`.
* `404 Not Found`: Target SID not in registry OR no existing export found for that DU.

---

## 🔍 Task Status API
Check the progress or result of a background deployment task.

* **Endpoint:** `GET /api/v1/du-automation/task-status/<task_id>/`

### 📤 Response Example
```json
{
  "status": "SUCCESS",
  "task_type": "IMPORT",
  "filename": "HANA_SIT_AM_TEN_RISE_20240414.tgz",
  "error_message": "System: OAF - Success: True - Output: Import complete...",
  "created_at": "2024-04-14T12:00:00Z"
}
```

**Statuses:** `PENDING`, `RUNNING`, `SUCCESS`, `FAILURE`.

---

## 🔄 Systems Registry Sync
Trigger a refresh of the internal SAP systems list from HAC's own data.

* **Endpoint:** `POST /api/v1/du-automation/sync-systems/`
* **Response:** `{"message": "Systems synchronized successfully"}`
