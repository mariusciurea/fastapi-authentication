# fastapi_authentication

A FastAPI demo project with classic authentication (`username/password`) and machine-to-machine (`client_credentials`) authentication, plus a protected command endpoint.

## What this project does

- issues user tokens at `POST /auth/token`
- issues M2M tokens for agents at `POST /auth/m2m-token`
- allows `GET /me` only for human users
- allows `GET /execute-command` only for M2M tokens
- validates that the command starts with `show`

## Main structure

- `src/service.py` - FastAPI application entrypoint
- `src/routers/auth_router.py` - token endpoints
- `src/routers/get_me_router.py` - `/me` endpoint
- `src/routers/execute_command_router.py` - `/execute-command` endpoint
- `src/auth/auth.py` - auth helpers, token validation, human/machine guards
- `src/data_models/models.py` - Pydantic models
- `src/settings.py` - settings, demo users, demo M2M clients
- `test_m2m.py` - M2M flow test script

## Run locally

1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install fastapi uvicorn python-multipart pydantic-settings "python-jose[cryptography]" argon2-cffi requests
```

3. Start the API:

```bash
uvicorn src.service:app --reload --port 8089
```

4. Open Swagger:

```text
http://localhost:8089/docs
```

## Endpoints

- `POST /auth/token`  
  classic user login (OAuth2 password form)

- `POST /auth/m2m-token`  
  M2M login (`client_id`, `client_secret`, `grant_type=client_credentials`)

- `GET /me`  
  available only for user tokens (human-only)

- `GET /execute-command?device=...&command=...`  
  available only for M2M tokens (machine-only), and `command` must start with `show`

## curl examples

### 1) Get an M2M token

```bash
curl -X POST "http://localhost:8089/auth/m2m-token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "client_id=adk-agent-orchestrator&client_secret=AgentSecret_123&grant_type=client_credentials"
```

### 2) Call execute-command (valid)

```bash
curl "http://localhost:8089/execute-command?device=router-1&command=show%20version" \
  -H "Authorization: Bearer <ACCESS_TOKEN>"
```

### 3) Call execute-command (invalid)

```bash
curl "http://localhost:8089/execute-command?device=router-1&command=restart" \
  -H "Authorization: Bearer <ACCESS_TOKEN>"
```

The response will be a validation error, because only commands starting with `show` are allowed.

## Test script

Run the included script:

```bash
python test_m2m.py
```

The script:
- obtains an M2M token
- tests `/execute-command`
- verifies that `/me` is blocked for M2M tokens (403)

## Demo data

`src/settings.py` currently contains hardcoded demo data:
- users (`USER`)
- M2M clients (`M2M_CLIENTS`)
- `SECRET_KEY`

For production:
- move secrets to environment variables / a secret manager
- do not keep credentials in code
- use key rotation and rotation policies
