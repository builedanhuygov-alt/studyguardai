# HTTP API Mapping

The stable application API is the `StudyGuardService` facade
(`studyguard/api/service.py`), which returns plain JSON-serializable dicts. A
thin HTTP layer (FastAPI/Flask) is a **documented extension point**: each route
maps 1:1 to a service method, so the transport carries no business logic.

| Method & path | Service call | Returns |
| --- | --- | --- |
| `GET /sources` | `list_sources()` | source list with consent/health |
| `POST /sources/{key}` | `connect_source(key, **config)` | connection status |
| `DELETE /sources/{key}` | `disconnect_source(key)` | status |
| `POST /consent/{key}` | `grant_consent(key)` | consent status |
| `DELETE /consent/{key}` | `revoke_consent(key)` | consent status |
| `GET /sessions` | `get_sessions()` | per-day summaries |
| `GET /timeline` | `get_timeline()` | per-day metric points |
| `GET /analytics` | `get_analytics()` | days + trends + streak |
| `GET /insights` | `get_insights()` | observations + inference + recs |
| `GET /recommendations` | `get_recommendations()` | coach recommendations |
| `GET /reports?period=&audience=` | `get_report(period=, audience=)` | structured report + markdown |
| `GET /data/export` | `export_data()` | all stored samples |
| `DELETE /data` | `delete_data()` | number deleted |

## Example adapter (FastAPI — illustrative, not shipped)
```python
from fastapi import FastAPI
from studyguard.api import StudyGuardService

app = FastAPI()
service = StudyGuardService()

@app.get("/analytics")
def analytics() -> dict:
    return service.get_analytics()

@app.post("/sources/{key}")
def connect(key: str) -> dict:
    service.grant_consent(key)
    return service.connect_source(key)
```
The adapter is intentionally trivial because all logic lives in the service.
