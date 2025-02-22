#!/usr/bin/env python3

import json, logging, os, requests
from base64 import b64encode
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import urlencode

from config import *


def get_jwt(filepath: str | Path = ".JWT") -> str | None:
    token_key = "id_token"
    sandbox_endpoint = (
        "https://auth.inditex.com:443/openam/oauth2/itxid/itxidmp/sandbox/access_token"
    )
    prod_endpoint = (
        "https://auth.inditex.com:443/openam/oauth2/itxid/itxidmp/access_token"
    )

    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            try:
                content = json.load(f)
            except json.decoder.JSONDecodeError:
                logging.error("Error: JWT file is corrupted.")
                return None

            if (
                datetime.fromisoformat(content["timestamp"])
                + timedelta(seconds=content["expires_in"])
                > datetime.now()
            ):
                logging.debug(f"Token read from file")
                return content[token_key]

    response = requests.post(
        prod_endpoint
        + "?"
        + urlencode(
            {"grant_type": "client_credentials", "scope": "technology.catalog.read"}
        ),
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"Basic {b64encode(f'{PUBLIC}:{SECRET}'.encode()).decode()}",
            "User-Agent": "PostmanRuntime/7.43.0",
        },
    )

    logging.debug(response)
    logging.debug(response.text)

    if response.status_code == 200:
        with open(".JWT", "w") as f:
            content = response.json()
            content["timestamp"] = datetime.now().isoformat()
            json.dump(content, f)
            logging.debug(f"Token written to file")

        return response.json()[token_key]

    return None


def get_img_products(jwt: str, img_url: str) -> dict:
    sandbox_endpoint = "https://api-sandbox.inditex.com/pubvsearch-sandbox/products"
    prod_endpoint = "https://api.inditex.com/pubvsearch/products"

    response = requests.get(
        prod_endpoint + "?image=" + img_url,
        headers={
            "Authorization": f"Bearer {jwt}",
            "Content-Type": "application/json",
            "User-Agent": "PostmanRuntime/7.43.0",
        },
    )

    logging.debug(response)
    logging.debug(response.text)

    return response.json()


if __name__ == "__main__":
    jwt = get_jwt()

    if not jwt:
        logging.error("Error: JWT could not be retrieved.")
        exit(1)

    img = "https://i.pinimg.com/originals/08/ff/da/08ffda7169479a93e97fc18a5bb20c8d.jpg"

    zara_products = get_img_products(jwt=jwt, img_url=img)

    print(json.dumps(zara_products, indent=4))

    for product in zara_products:
        print(product["name"], end="   ->   ")
        print(product["price"]["value"]["current"])
        print(product["link"])
        print("---\n")
