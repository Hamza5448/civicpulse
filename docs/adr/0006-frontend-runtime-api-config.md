# ADR 0006: Runtime Frontend API Configuration

- Status: Accepted
- Date: 2026-09-28

## Context

Vite values can be compiled into the browser bundle, which would make a frontend build environment-specific. The frontend needs to use the same build against different backend origins without exposing credentials or rebuilding for each environment.

## Decision

Load `/config.js` before the application bundle. It defines the public `apiBaseUrl`, defaulting to the relative `/api` path. The Vite development server proxies `/api`, `/health`, and `/ready` to the local backend. A later container entrypoint may replace `/config.js` at startup without changing the application bundle.

## Consequences

- No backend URL or secret is baked into the TypeScript bundle.
- Development uses the existing backend routes without CORS-specific frontend work.
- Runtime deployment only needs to provide a public API base URL; it must never put credentials in this file.
