import logging, os

with open(".env", "r") as f:
    env = dict([line.strip().split("=") for line in f.readlines()])

if os.getenv("PUBLIC") is None:
    os.environ["PUBLIC"] = env["PUBLIC"]
if os.getenv("SECRET") is None:
    os.environ["SECRET"] = env["SECRET"]
if os.getenv("LOGLEVEL") is None:
    os.environ["LOGLEVEL"] = env.get("LOGLEVEL", "INFO")

PUBLIC = os.getenv("PUBLIC")
SECRET = os.getenv("SECRET")

logging.basicConfig(
    level=os.getenv("LOGLEVEL", "INFO").upper(),
    format="%(asctime)s [%(levelname)s] (%(name)s) %(message)s",
)
