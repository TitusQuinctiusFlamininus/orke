from fastapi import FastAPI
from agent import run_agent

app = FastAPI()


@app.post("/run")
async def run(url: str):
    result = await run_agent(url)
    return result