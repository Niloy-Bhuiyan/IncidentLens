# ADR-007: Deployment Strategy

## Context
Next.js and FastAPI have first-class Vercel runtimes but different project roots/configuration. The no-cost demo must survive serverless cold starts without persistent infrastructure.

## Decision
Deploy two Vercel projects from the private monorepo: frontend rooted at `frontend/`, backend rooted at `backend/`. Point the frontend public API URL to the backend and restrict backend CORS to the frontend. Bundle and lazily index immutable demo evidence.

## Alternatives considered
Vercel Services can combine multiple services in one project but adds newer platform configuration and availability risk. A separate host increases operational surface. Reimplementing the API in Next.js violates the FastAPI requirement. Hosted PostgreSQL/pgvector adds cost/configuration before v1 needs durability.

## Why
Separate mature runtimes are easy to inspect, independently roll back, and align with framework defaults.

## Trade-offs
Two deployments and cross-origin configuration are required; in-process state is not durable.

## Consequences
Production verification covers both URLs and CORS. The frontend URL is the public product URL; docs disclose stateless behavior.

