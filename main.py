from typing import Union

from fastapi import FastAPI

from link_verifying_agent import LinkVerifyingAgent
from query_parse_agent import QueryParsingAgent

app = FastAPI()

# We will pass a query string parameter here with what we want to parse
# http://127.0.0.1:8000/?q=somequery
@app.get("/")
async def read_root(q: Union[str, None] = None):
    return {"request": q}

@app.get("/test")
async def test_endpoint():
    message = "You just won the lottery! Visit www.getrichnowwithbitcoin.co/lottery to claim your prize"
    return await handle_query(message)

async def handle_query(query: str ):
    parsed_query = QueryParsingAgent().parse_query(query)
    link_info = LinkVerifyingAgent().verify_links(parsed_query)

    return {"test": link_info}

