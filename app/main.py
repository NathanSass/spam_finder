from typing import Union
from fastapi import FastAPI
from agents.link_verifying_agent import LinkVerifyingAgent
from agents.query_parse_agent import QueryParsingAgent

from score_evaluator.score_evaluator import ScoreEvaluator

app = FastAPI()

# We will pass a query string parameter here with what we want to parse
#   uvicorn main:app --reload
#   GET http://127.0.0.1:8000/query?message="You have an important message waiting in your Chase Secure Message Center. <https://ad.doubleclick.verysafelink.com/afj40923|Click here!>.
@app.get("/")
async def echo(q: Union[str, None] = None):
    return {"request": q}

@app.get("/query")
async def query(message: Union[str, None] = None):
    return await handle_query(message)

@app.get("/test")
async def test_endpoint():
    query = "You just won the lottery! Visit www.getrichnowwithbitcoin.co/lottery to claim your prize"
    return await handle_query(query)

async def handle_query(query: str ):
    """
    Steps:
    1. Parse the input (text message, email, etc.)
    2. Verify the links within the input
    3. 
    """
    parsed_query = QueryParsingAgent().parse_query(query)
    link_info = LinkVerifyingAgent().verify_links(parsed_query)
    link_info['is_spam'] = ScoreEvaluator().is_spam(link_info['categories'])
    
    return link_info

