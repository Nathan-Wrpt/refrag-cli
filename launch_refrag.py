import argparse
import asyncio
import json
import os
import subprocess
import sys

import requests
import websockets
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://api-k8s.refrag.gg"

COMMON_HEADERS = {
    "accept": "application/json, text/plain, */*",
    "content-type": "application/json",
    "origin": "https://play.refrag.gg",
    "referer": "https://play.refrag.gg/",
    "x-game": "cs2",
    "x-team-id": TEAM_ID,
}


def sign_in(email: str, password: str) -> dict:
    """Authenticate and return auth headers."""
    resp = requests.post(
        f"{BASE_URL}/auth/sign_in",
        json={"email": email, "password": password},
        headers=COMMON_HEADERS,
    )
    if resp.status_code != 200:
        print(f"[ERROR] Login failed ({resp.status_code}): {resp.text}")
        sys.exit(1)

    h = resp.headers
    auth_token = h.get("access-token")
    client = h.get("client")
    expiry = h.get("expiry")
    uid = h.get("uid")
    token_type = h.get("token-type", "Bearer")

    # Build the encoded bearer token from the response body if available
    body = resp.json()
    bearer = body.get("data", {}).get("token") or ""

    print(f"[OK] Logged in as {uid}")
    return {
        "access-token": auth_token,
        "client": client,
        "expiry": expiry,
        "token-type": token_type,
        "uid": uid,
        "authorization": f"{token_type} {bearer}" if bearer else "",
    }


async def wait_for_server_ws(auth_headers: dict, server_id: int, timeout: int = 300) -> dict:
    """Listen on the ActionCable WebSocket and return server data once it is fully started."""
    url = "wss://api-k8s.refrag.gg/cable"
    ws_headers = {
        "Origin": "https://play.refrag.gg",
        "access-token": auth_headers.get("access-token", ""),
        "client": auth_headers.get("client", ""),
        "uid": auth_headers.get("uid", ""),
        "token-type": auth_headers.get("token-type", "Bearer"),
        "expiry": auth_headers.get("expiry", ""),
        "authorization": auth_headers.get("authorization", ""),
    }
    identifier = json.dumps({"channel": "CsServerChannel", "team_id": int(TEAM_ID)})

    dots = 0
    async with websockets.connect(
        url,
        additional_headers=ws_headers,
        subprotocols=["actioncable-v1-json"],
        open_timeout=30,
    ) as ws:
        # Wait for welcome handshake
        raw = await asyncio.wait_for(ws.recv(), timeout=30)
        if json.loads(raw).get("type") == "welcome":
            await ws.send(json.dumps({"command": "subscribe", "identifier": identifier}))

        deadline = asyncio.get_event_loop().time() + timeout
        while asyncio.get_event_loop().time() < deadline:
            remaining = deadline - asyncio.get_event_loop().time()
            try:
                raw = await asyncio.wait_for(ws.recv(), timeout=min(remaining, 30))
            except asyncio.TimeoutError:
                break

            msg = json.loads(raw)

            # Ignore pings and subscription confirmations
            if msg.get("type") in ("ping", "confirm_subscription", "welcome"):
                dots += 1
                print(f"\r[INFO] Waiting for server to be ready{'.' * (dots % 4):<3}", end="", flush=True)
                continue

            # Look for server list payload
            servers = msg.get("message", {}).get("servers")
            if servers:
                for server in servers:
                    if server.get("id") == server_id:
                        status = server.get("status", "")
                        if status not in ("starting", "booting", "provisioning", ""):
                            print()  # newline after dots
                            return server
                        else:
                            dots += 1
                            print(f"\r[INFO] Waiting for server to be ready{'.' * (dots % 4):<3}", end="", flush=True)

    print()
    print("[ERROR] Timed out waiting for server to start.")
    sys.exit(1)


async def start_server(auth_headers: dict, map_name: str, mod: str) -> None:
    """Start a new CS2 Refrag server."""
    headers = {**COMMON_HEADERS, **auth_headers}

    payload = {
        "server_location_id": LOCATION_ID,
        "game": "cs2",
        "betaServer": False,
        "secureServer": False,
        "is_assessment": False,
        "launch_settings": {
            "mod": mod,
            "map": map_name,
        },
    }

    print(f"[INFO] Starting server  map={map_name}  mod={mod} ...")
    resp = requests.post(
        f"{BASE_URL}/cs_servers/start_new_server",
        json=payload,
        headers=headers,
    )

    if resp.status_code in (200, 201):
        data = resp.json()
        server_id = data.get("id")
        if not server_id:
            print("[ERROR] No server ID in response.")
            sys.exit(1)

        print(f"[INFO] Server queued (id={server_id}), waiting for it to be ready...")
        data = await wait_for_server_ws(auth_headers, server_id)

        print("[OK] Server is ready!")
        ip = data.get("ip", "")
        port = data.get("port", "")
        password = data.get("password", "")
        status = data.get("status", "")
        if ip and port:
            connect = f"connect {ip}:{port}"
            if password:
                connect += f"; password {password}"
            print("connect string:")
            print(connect)
            subprocess.run("clip", input=connect.encode(), check=True)
            print("[OK] Connect string copied to clipboard!")
    else:
        print(f"[ERROR] Failed to start server ({resp.status_code}): {resp.text}")
        print("A server may already be running, check that you don't have an active server on your Refrag dashboard.")
        sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser(description="Launch a CS2 Refrag server via API")
    parser.add_argument("--map", dest="map_name", default="de_dust2",
                        help="Map name (default: de_dust2)")
    parser.add_argument("--mod", dest="mod", default="nadr",
                        help="Game mode / mod (default: nadr)")
    args = parser.parse_args()

    email = os.getenv("MAIL") or os.getenv("EMAIL")
    password = os.getenv("PASSWORD")

    if not email or not password:
        print("[ERROR] MAIL and PASSWORD must be set in the .env file.")
        sys.exit(1)

    auth_headers = sign_in(email, password)
    map_name = args.map_name
    if not map_name.startswith("de_"):
        map_name = "de_" + map_name
    asyncio.run(start_server(auth_headers, map_name=args.map_name, mod=args.mod))


if __name__ == "__main__":
    main()

