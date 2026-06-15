# Production Deployment

This guide documents the minimal production scaffolding for deploying the
Technology Research & Evaluation Agent as:

```text
Vercel frontend + single-node Docker backend on Alibaba Cloud ECS
```

It does not require changes to the Gateway, worker runtime, Technology
Evaluation pipeline, or EvaluationReport viewer logic.

## Recommended Architecture

```text
Browser
  -> https://app.example.com        Vercel Next.js frontend
  -> /api/*                         Vercel server-side rewrites
  -> https://api.example.com        ECS nginx reverse proxy
  -> gateway:8001                   FastAPI Gateway + agent runtime
  -> /data/deer-flow                persistent runtime data and artifacts
```

Use Vercel for the frontend and Alibaba Cloud ECS for the backend because the
backend needs long-running SSE connections, writable artifact storage, optional
Docker sandbox access, and a stable single worker. The existing Docker backend
stack already assumes a single Gateway worker for run state and stream
reconnect correctness.

## Alternative Architecture

For a simpler single-machine deployment, run the full Docker stack on ECS:

```text
Browser
  -> https://app.example.com or https://deerflow.example.com
  -> ECS nginx
  -> frontend:3000 + gateway:8001
```

This keeps frontend and backend same-origin behind nginx. It is easier to
operate than split-origin hosting, but you give up Vercel previews and managed
Next.js hosting.

## Frontend on Vercel

Create a Vercel project with:

```text
Root Directory: frontend
Install Command: pnpm install --frozen-lockfile
Build Command: pnpm build
Output: Next.js default
```

Set this Vercel environment variable:

```env
DEER_FLOW_INTERNAL_GATEWAY_BASE_URL=https://api.example.com
```

Do not set these by default:

```env
NEXT_PUBLIC_BACKEND_BASE_URL
NEXT_PUBLIC_LANGGRAPH_BASE_URL
```

Leaving the public backend variables unset keeps browser API calls same-origin
under `/api/*`. The frontend's `next.config.js` rewrites those API requests to
`DEER_FLOW_INTERNAL_GATEWAY_BASE_URL` on the server side, which avoids
split-origin cookie and CSRF problems.

Only set `NEXT_PUBLIC_BACKEND_BASE_URL` and `NEXT_PUBLIC_LANGGRAPH_BASE_URL`
when you intentionally want the browser to call the Gateway origin directly.
If you do that, also set `GATEWAY_CORS_ORIGINS` on the backend to the exact
Vercel app origin.

## Backend on Alibaba Cloud ECS

1. Install Docker and Docker Compose on the ECS instance.
2. Clone the repository.
3. Create a persistent runtime directory:

```bash
sudo mkdir -p /data/deer-flow
sudo chown -R "$USER":"$USER" /data/deer-flow
```

4. Create production env and config files from the templates:

```bash
cp docker/.env.production.example docker/.env.production
cp backend/config.production.example.yaml /data/deer-flow/config.yaml
printf '{}\n' > /data/deer-flow/extensions_config.json
touch .env
touch frontend/.env
```

5. Edit `docker/.env.production` and `/data/deer-flow/config.yaml`.
   Replace every `replace_me` value. Set `DEER_FLOW_REPO_ROOT` to the absolute
   repository path on the ECS host. `.env` and `frontend/.env` can remain empty
   for the Vercel frontend + ECS backend topology; they only satisfy the base
   Compose file's local env-file declarations. Do not commit these files.

6. Start the backend stack:

```bash
docker compose \
  --env-file docker/.env.production \
  -f docker/docker-compose.yaml \
  -f docker/docker-compose.production.yaml \
  up -d --build nginx gateway
```

For the full single-host Docker deployment, include `frontend` as well:

```bash
docker compose \
  --env-file docker/.env.production \
  -f docker/docker-compose.yaml \
  -f docker/docker-compose.production.yaml \
  up -d --build
```

7. Check Gateway health:

```bash
curl -fsS https://api.example.com/health
```

## Persistent Data

`DEER_FLOW_HOME` must point to a persistent disk directory. The recommended ECS
path is:

```env
DEER_FLOW_HOME=/data/deer-flow
```

DeerFlow stores runtime data, SQLite state, user-scoped thread directories,
uploads, and generated artifacts under this tree. EvaluationReport JSON and
Markdown artifacts are written under each thread's `user-data/outputs`
directory. If this path is not persisted, reports disappear after container or
host rebuilds.

Back up `/data/deer-flow` before upgrades.

## DeepSeek Secrets

Do not put real API keys in `config.yaml` or source control. The production
config template references:

```yaml
api_key: $DEEPSEEK_API_KEY
```

Set the real value only in `docker/.env.production` or in your ECS secret
injection mechanism.

## Production Config

Use `backend/config.production.example.yaml` as the starting point. It keeps the
deployment single-node with SQLite by default and configures:

- DeepSeek through an OpenAI-compatible `ChatOpenAI` provider
- persistent SQLite under `.deer-flow/data`
- production-friendly upload limits
- Docker/AIO sandbox recommendation
- built-in guardrails to deny high-risk tools by default
- loop detection and circuit breaker protections

If you later need multi-node or higher write concurrency, move `database` to
Postgres and put `DATABASE_URL` in environment secrets.

## Auth Bootstrap

Do not enable `DEER_FLOW_AUTH_DISABLED` in production. Set:

```env
DEER_FLOW_ENV=production
ENVIRONMENT=production
```

On first boot, visit:

```text
https://app.example.com/setup
```

Create the first admin account, then sign in normally. Keep
`AUTH_JWT_SECRET` stable across restarts.

## Live Smoke Test

After deployment:

1. Sign in as admin.
2. Start a new chat.
3. Ask:

```text
Evaluate LangGraph for long-running AI agent workflows.
```

4. Confirm the run completes.
5. Open the generated artifacts.
6. Confirm the Markdown report renders normally.
7. Confirm the EvaluationReport JSON artifact opens in the specialized viewer
   with verdict summary, scorecard, evidence matrix, risks, alternatives, and
   references.

This smoke test validates the deployed pipeline path. It does not guarantee
report quality, provider stability, or fixed token cost.

## Nginx Production Profile

`docker/nginx/nginx.production.conf` adds:

- rate limiting for run creation and stream paths
- SSE-safe proxy buffering settings
- long-running request timeouts
- basic security headers
- `client_max_body_size 100M`

It is enabled by `docker/docker-compose.production.yaml`. The default
`docker/nginx/nginx.conf` is unchanged for local development.

## Common Risks

- No run rate limit: public traffic can burn DeepSeek credits quickly.
- No persistent disk: SQLite data and artifacts disappear on redeploy.
- Exposed keys: never commit `.env`, `config.yaml`, or provider secrets.
- Disabled auth: never set `DEER_FLOW_AUTH_DISABLED=1` for shared or
  production deployments.
- Docker socket risk: AIO sandbox may require Docker access. Treat the Gateway
  container as privileged infrastructure and avoid untrusted multi-tenant use.
- Multiple Gateway workers: keep `GATEWAY_WORKERS=1` unless shared run state
  and stream bridge infrastructure are added.
- Split-origin browser calls: only use direct public backend URLs when CORS,
  cookies, and CSRF have been verified end to end.
