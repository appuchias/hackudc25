import logging, os
from hashlib import sha256

from flask import Flask, request, render_template, send_file
from werkzeug.utils import secure_filename

from config import *
from api import get_jwt, get_img_products

UPLOAD_FOLDER = "uploads/"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}

app = Flask(__name__, template_folder="templates", static_folder="static")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.url_map.strict_slashes = False


@app.route("/")
def index():
    return render_template("inicio.html")


@app.route("/tool")
def tool():
    return render_template("api.html")


@app.route("/tool/search", methods=["POST"])
def search():
    logging.debug(request.files)

    # Image
    image = request.files["image"]
    image_extension = (image.filename if image.filename else ".").split(".")[-1]
    image_hash = sha256(image.read()).hexdigest()
    image.seek(0)  # Reset file pointer
    image.save(UPLOAD_FOLDER + image_hash + "." + secure_filename(image_extension))

    img_url = (
        request.url_root + "img/" + image_hash + "." + secure_filename(image_extension)
    )

    logging.debug(f"Image available at {img_url}")

    # API
    jwt = get_jwt()
    if not jwt:
        logging.error("Error: JWT could not be retrieved.")
        return render_template("api.html")

    products = get_img_products(jwt, img_url)

    logging.debug(products)

    return image_hash


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
    return render_template("vision_general.html")
