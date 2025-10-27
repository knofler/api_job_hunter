# AI Matching Job API

This is the backend API for the AI Matching Job application. It is built using FastAPI and connects to MongoDB for data storage.

## Features
- User management
- Job ranking and matching
- Health check endpoint
- Recruiter workflow AI orchestration with multi-provider LLM support

## Requirements
- Python 3.12+
- Docker and Docker Compose
- Fly.io CLI (for deployments)

## Local Development
1. Copy the example environment file and update values as needed:
   ```bash
   cp .env.example .env
   ```
2. Launch the API and MongoDB containers:
   ```bash
   docker compose up --build
   ```
3. Access the FastAPI docs at `http://localhost:8000/docs` once the stack is running.

### LLM configuration

The recruiter workflow endpoints call external LLM APIs. Provide credentials via environment variables or the admin
settings API:

- `LLM_DEFAULT_PROVIDER` (`openai`, `anthropic`, `google`, `deepseek`, `bedrock`)
- `OPENAI_API_KEY`, `OPENAI_MODEL`, `OPENAI_BASE_URL`
- `ANTHROPIC_API_KEY`, `ANTHROPIC_MODEL`
- `GOOGLE_GEMINI_API_KEY`, `GOOGLE_GEMINI_MODEL`
- `DEEPSEEK_API_KEY`, `DEEPSEEK_MODEL`, `DEEPSEEK_BASE_URL`
- `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_SESSION_TOKEN`, `AWS_REGION`, `BEDROCK_MODEL`

Admins can update provider configurations (including per-step overrides) via `PUT /admin/llm/settings`. To inspect
available providers use `GET /admin/llm/providers`.

## Testing
Run the pytest suite from the repository root:
```bash
cd ai-matching-job-api
pip install -r requirements.txt
pip install -r requirements.dev.txt
pytest
```

## Deploying to Fly.io
1. Create a Fly.io app in the `syd` region and note the app name.
2. Set the required GitHub secrets:
   - `FLY_API_TOKEN`: token generated via `fly auth token`.
   - `FLY_APP_NAME`: Fly.io app slug used during deployment.
3. Configure runtime secrets (such as `MONGO_URI`) using `fly secrets set`.
4. Merges to `main` trigger `.github/workflows/api-ci.yml`, which runs tests, builds the container, and deploys to Fly.io.