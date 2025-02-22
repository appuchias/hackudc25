with open(".env", "r") as f:
    for line in f:
        key, value = line.strip().split("=")
        globals()[key] = value
