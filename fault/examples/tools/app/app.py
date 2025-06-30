import os

import httpx
from fastapi import FastAPI

UPSTREAM_URL = os.getenv("UPSTREAM_URL", "https://jsonplaceholder.typicode.com")

app = FastAPI()


@app.get("/")
def index():
    return httpx.get(f"{UPSTREAM_URL}/todos/1", headers={
        "Host": "jsonplaceholder.typicode.com"
    }).json()
