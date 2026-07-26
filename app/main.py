from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from app.agents.factory import AgentFactory
from app.agents.registry import DEFAULT_AGENT, AgentRegistry

NAME = "DevOps Mentor AI Platform"
VERSION = "1.1.0"

app = FastAPI(
    title=NAME,
    version=VERSION,
)


class ChatRequest(BaseModel):
    """A question for one of the agents."""

    message: str
    agent: str = Field(
        default=DEFAULT_AGENT,
        description="Agent that answers the question. Defaults to the teacher.",
    )


@app.get("/")
def root() -> dict[str, str]:
    """Return the name and the state of the service."""
    return {
        "name": NAME,
        "status": "running",
        "version": VERSION,
    }


@app.get("/health")
def health() -> dict[str, str]:
    """Return the liveness of the service."""
    return {"status": "ok"}


@app.get("/agents")
def agents() -> dict[str, object]:
    """List the registered agents with their capabilities."""
    registered = []

    for name in AgentRegistry.available():
        agent_class = AgentRegistry.get(name)
        registered.append(
            {
                "name": agent_class.name or name,
                "description": agent_class.description,
                "capabilities": list(agent_class.capabilities),
            }
        )

    return {"default": DEFAULT_AGENT, "agents": registered}


@app.post("/chat")
def chat(request: ChatRequest) -> dict[str, str]:
    """Answer a question with the requested agent.

    Raises:
        HTTPException: 400 if the requested agent is not registered.
    """
    try:
        agent = AgentFactory.create(request.agent)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

    return {
        "answer": agent.ask(request.message),
        "agent": agent.name,
    }
