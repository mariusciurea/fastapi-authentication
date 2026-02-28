import argparse
import sys
from pydantic import ValidationError

import requests


def get_m2m_token(base_url: str, client_id: str, client_secret: str) -> str:
    url = f"{base_url}/auth/m2m-token"
    data = {
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "client_credentials",
    }
    response = requests.post(url, data=data, timeout=15)
    if response.status_code != 200:
        raise RuntimeError(
            f"Token request failed ({response.status_code}): {response.text}"
        )
    payload = response.json()
    return payload["access_token"]


def call_execute_command(base_url: str, token: str, device: str, command: str) -> requests.Response:
    url = f"{base_url}/execute-command"
    headers = {"Authorization": f"Bearer {token}"}
    params = {"device": device, "command": command}
    return requests.get(url, headers=headers, params=params, timeout=15)


def call_me(base_url: str, token: str) -> requests.Response:
    url = f"{base_url}/me"
    headers = {"Authorization": f"Bearer {token}"}
    return requests.get(url, headers=headers, timeout=15)


def main() -> int:
    parser = argparse.ArgumentParser(description="Test M2M flow for FastAPI endpoint")
    parser.add_argument("--base-url", default="http://localhost:8089")
    parser.add_argument("--client-id", default="adk-agent-orchestrator")
    parser.add_argument("--client-secret", default="AgentSecret_123")
    parser.add_argument("--device", default="router-1")
    parser.add_argument("--command", default="rst interface")
    args = parser.parse_args()

    try:
        token = get_m2m_token(args.base_url, args.client_id, args.client_secret)
        print("OK: m2m token obtained")

        execute_response = call_execute_command(
            args.base_url, token, args.device, args.command
        )
        print(f"/execute-command status: {execute_response.status_code}")
        print(f"/execute-command body: {execute_response.text}")

        me_response = call_me(args.base_url, token)
        print(f"/me status (should be 403): {me_response.status_code}")
        print(f"/me body: {me_response.text}")

        if execute_response.status_code != 200:
            return 1
        if me_response.status_code != 403:
            return 1
        return 0
    except ValidationError as e:
        print(f"EROR: {e}")
    except Exception as e:
        print(f"ERROR: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
