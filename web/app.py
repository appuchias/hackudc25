import logging, os
from hashlib import sha256

from flask import Flask, request, render_template, send_file
from werkzeug.utils import secure_filename

from config import *
from api import get_jwt, get_img_products

UPLOAD_FOLDER = "uploads/"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}

# a.k.a. "honestidad" (usar resultados precalculados por problemas con la API)
MOCK = True

app = Flask(__name__, template_folder="templates", static_folder="static")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.url_map.strict_slashes = False

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


@app.route("/")
def index():
    return render_template("inicio.html")


@app.route("/tool")
def tool():
    return render_template("api.html")


@app.route("/tool/search", methods=["POST"])
def search():
    # Image
    image = request.files["image"]
    image_hash = sha256(image.read()).hexdigest()
    if MOCK:
        img_url = {
            "f2c655ff37ee2f15149c19f14378fc5cdf537051d819af4b49212e3bd4c42f97": "https://i.imgur.com/OOcMXHd.jpeg",  # Yellow
            "f4f6597b67c5f6f67d5394aef3ac09908232fdb6f2266b5b29056ff81fc083da": "https://i.imgur.com/eBIzlL8.jpeg",  # Black
        }[image_hash]
    else:
        image_extension = (image.filename if image.filename else ".").split(".")[-1]
        image.seek(0)  # Reset file pointer
        image.save(UPLOAD_FOLDER + image_hash + "." + secure_filename(image_extension))

        img_url = (
            request.url_root
            + "img/"
            + image_hash
            + "."
            + secure_filename(image_extension)
        )

    logging.debug(f"Image available at {img_url}")

    # API
    jwt = get_jwt()
    if not jwt:
        logging.error("Error: JWT could not be retrieved.")
        return render_template("api.html")

    products = get_img_products(jwt, img_url)

    if not products and MOCK:
        if (
            image_hash
            == "f2c655ff37ee2f15149c19f14378fc5cdf537051d819af4b49212e3bd4c42f97"
        ):
            products = [
                {
                    "id": "416257082",
                    "name": "3-PACK OF PLAIN T-SHIRTS",
                    "price": {
                        "currency": "EUR",
                        "value": {"current": 12.95, "original": None},
                    },
                    "link": "https://zara.com/es/en/-P01716307.html",
                    "brand": "zara",
                },
                {
                    "id": "421183789",
                    "name": "ZARA TIMELESZ  - EMBROIDERED DETAIL SWEATSHIRT",
                    "price": {
                        "currency": "EUR",
                        "value": {"current": 15.95, "original": None},
                    },
                    "link": "https://zara.com/es/en/-P05643545.html",
                    "brand": "zara",
                },
                {
                    "id": "441256431",
                    "name": "STRIPED SWEATSHIRT",
                    "price": {
                        "currency": "EUR",
                        "value": {"current": 15.95, "original": None},
                    },
                    "link": "https://zara.com/es/en/-P00531602.html",
                    "brand": "zara",
                },
                {
                    "id": "423155777",
                    "name": "PLAIN SWEATSHIRT",
                    "price": {
                        "currency": "EUR",
                        "value": {"current": 10.95, "original": None},
                    },
                    "link": "https://zara.com/es/en/-P00257601.html",
                    "brand": "zara",
                },
                {
                    "id": "427292922",
                    "name": "PLAIN T-SHIRT WITH LABEL",
                    "price": {
                        "currency": "EUR",
                        "value": {"current": 10.95, "original": None},
                    },
                    "link": "https://zara.com/es/en/-P09007620.html",
                    "brand": "zara",
                },
            ]
        elif (
            image_hash
            == "f4f6597b67c5f6f67d5394aef3ac09908232fdb6f2266b5b29056ff81fc083da"
        ):
            products = [
                {
                    "id": "410575278",
                    "name": "LEATHER EFFECT BOMBER JACKET",
                    "price": {
                        "currency": "EUR",
                        "value": {"current": 39.95, "original": None},
                    },
                    "link": "https://zara.com/es/en/-P03918327.html",
                    "brand": "zara",
                },
                {
                    "id": "410570346",
                    "name": "FAUX LEATHER BIKER JACKET",
                    "price": {
                        "currency": "EUR",
                        "value": {"current": 55.95, "original": None},
                    },
                    "link": "https://zara.com/es/en/-P08491400.html",
                    "brand": "zara",
                },
                {
                    "id": "413695616",
                    "name": "BASIC COTTON BLEND TRAINING T-SHIRT",
                    "price": {
                        "currency": "EUR",
                        "value": {"current": 15.95, "original": None},
                    },
                    "link": "https://zara.com/es/en/-P00761400.html",
                    "brand": "zara",
                },
                {
                    "id": "413977344",
                    "name": "WASHED TRAINING T-SHIRT",
                    "price": {
                        "currency": "EUR",
                        "value": {"current": 22.95, "original": None},
                    },
                    "link": "https://zara.com/es/en/-P05643400.html",
                    "brand": "zara",
                },
                {
                    "id": "423159071",
                    "name": "MEDIUM WEIGHT T-SHIRT",
                    "price": {
                        "currency": "EUR",
                        "value": {"current": 25.95, "original": None},
                    },
                    "link": "https://zara.com/es/en/-P01501502.html",
                    "brand": "zara",
                },
            ]

    logging.debug(products)

    return render_template("resultados.html", products=products)


@app.route("/img/<filename>")
def img(filename):
    img_path = UPLOAD_FOLDER + filename

    if not os.path.exists(img_path):
        logging.error(f"Image {filename} not found")
        return "Not found", 404

    logging.debug(f"Image {img_path} requested")

    return send_file(img_path)


@app.route("/documentation")
def documentation():
    return render_template("documentacion.html")
