#!/usr/bin/env python3

import json, os, requests
from base64 import b64encode
from pathlib import Path
from urllib.parse import urlencode

from config import *


def get_jwt(filepath: str | Path = ".JWT") -> str | None:
    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            try:
                return json.load(f)["access_token"]
            except json.decoder.JSONDecodeError:
                print("Error: JWT file is corrupted.")
                return None

    response = requests.post(
        "https://auth.inditex.com:443/openam/oauth2/itxid/itxidmp/sandbox/access_token"
        + "?"
        + urlencode(
            {"grant_type": "client_credentials", "scope": "technology.catalog.read"}
        ),
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"Basic {b64encode(f'{PUBLIC}:{SECRET}'.encode()).decode()}",
            "User-Agent": "PostmanRuntime/7.26.8",
        },
    )

    if response.status_code == 200:
        with open(".JWT", "w") as f:
            json.dump(response.json(), f)

        return response.json()["access_token"]

    return None


if __name__ == "__main__":
    print(get_jwt())
