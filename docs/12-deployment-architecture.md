# Deployment Architecture

The private GitHub monorepo is deployed as two Vercel projects because separate project roots are the mature, independently debuggable path for Next.js and FastAPI. The product URL is the frontend; the backend has its own API URL.

```text
GitHub/private main
  ├─ frontend/ → Vercel Next.js project → product URL
  └─ repository root + api/index.py → Vercel Python/FastAPI project → API URL
```

The frontend project sets `NEXT_PUBLIC_API_BASE_URL` to the backend URL. Backend `INCIDENTLENS_ALLOWED_ORIGINS` lists only the product URL (plus localhost outside production). `INCIDENTLENS_LLM_PROVIDER=mock` is the public default; provider secrets are optional and backend-only.

The seeded corpus is bundled read-only with the backend project. Each cold start lazily indexes it in process. This avoids a paid database but means arbitrary investigations are not durable across instances. A future deployment can add PostgreSQL/pgvector adapters at the existing service/retrieval boundaries; no pgvector adapter is claimed in v1.

Verified production projects:

- product: `https://incidentlens-nine.vercel.app` (`incidentlens`, root `frontend`, Next.js);
- API: `https://incidentlens-api-delta.vercel.app` (`incidentlens-api`, repository root, FastAPI);
- both projects are connected to `Niloy-Bhuiyan/IncidentLens`; production public/runtime environment variables are stored in Vercel, not Git.

Rollout order is backend preview → API smoke → frontend preview with API URL → full smoke → production aliases. Rollback uses the previous verified Vercel deployment. Deployment URLs and measured status belong in the production smoke report, never inferred from CLI success alone.

