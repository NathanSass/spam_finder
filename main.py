from typing import Union

from fastapi import FastAPI

from link_verifying_agent import LinkVerifyingAgent

app = FastAPI()

# We will pass a query string parameter here with what we want to parse
# http://127.0.0.1:8000/?q=somequery
@app.get("/")
async def read_root(q: Union[str, None] = None):
    return {"request": q}

@app.get("/test")
async def test_endpoint():
    message = "You just won the lottery! Visit www.t.co/lottery to claim your prize"
    link_verifier = LinkVerifyingAgent()
    result = link_verifier.verify_link(message)
    return {"test": result}

