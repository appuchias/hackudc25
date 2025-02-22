import logging, os

from dotenv import load_dotenv

load_dotenv()

# with open(".env", "r") as f:
#     env = dict([line.strip().split("=") for line in f.readlines()])

PUBLIC = os.getenv("PUBLIC")
SECRET = os.getenv("SECRET")

logging.basicConfig(
    level=os.getenv("LOGLEVEL", "INFO").upper(),
    format="%(asctime)s [%(levelname)s] (%(name)s) %(message)s",
)
