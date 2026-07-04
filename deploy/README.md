# Production deployment (config — not executed in this repo's sandbox)

```bash
cd deploy
docker compose -f docker-compose.prod.yml up --build
# API via nginx:  http://localhost/api/v1/health
# Swagger:        http://localhost/docs
# Prometheus:     http://localhost:9090
# Grafana:        http://localhost:3000  (admin/admin)
```

Observability endpoints: `/metrics` (Prometheus scrape), `/api/v1/health`,
`/api/v1/readiness`, `/api/v1/liveness`. JSON logging via `STUDYGUARD_LOG_JSON=1`
(+ optional Sentry hook, see `docs/DEPLOYMENT.md`).

Status: ✅ Generated. ⚠ Requires Docker to build/run; not executed here.
