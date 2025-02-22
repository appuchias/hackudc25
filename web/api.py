#!/usr/bin/env python3

import json, logging, os, requests
from base64 import b64encode
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
                token = json.load(f)[token_key]
                logging.debug(f"Token read from file")
                return token
            except json.decoder.JSONDecodeError:
                logging.error("Error: JWT file is corrupted.")
                return None

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
            json.dump(response.json(), f)
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
    # img = "https://i.pinimg.com/736x/50/f8/45/50f8450d3305fb90a30dc387195ae023.jpg"
    # img = "https://images.unsplash.com/photo-1581655353564-df123a1eb820?q=80&w=1587&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D"

    zara_products = get_img_products(jwt=jwt, img_url=img)

    print(json.dumps(zara_products, indent=4))

    for product in zara_products:
        print(product["name"], end="   ->   ")
        print(product["price"]["value"]["current"])
        print(product["link"])
        print("---\n")
