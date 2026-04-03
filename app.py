from fastapi import FastAPI
from pydantic import BaseModel

from agent import root_agent

app = FastAPI()

class Request(BaseModel):
    message: str

@app.post("/chat")
async def chat(req: Request):
    response = root_agent.run(req.message)
    return {"response": response}