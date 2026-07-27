from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.agents.factory import AgentFactory
from app.agents.registry import AgentRegistry
from app.api.health import build_health
from app.config import settings

NAME = "DevOps Mentor AI Platform"
VERSION = "1.0.0"
API_V1_PREFIX = "/api/v1"

router = APIRouter()


class ChatRequest(BaseModel):
    """A question for one of the agents."""

    message: str
    agent: str = Field(
        default="",
        description=(
            "Agent that answers the question. Empty means the configured "
            "default agent, which keeps older clients working."
        ),
    )


class ChatResponse(BaseModel):
    """The answer and the agent that produced it."""

    answer: str
    agent: str


@router.get("/")
def root() -> dict[str, str]:
    """Return the name and the state of the service."""
    return {"name": NAME, "status": "running", "version": VERSION}


@router.get("/health")
def health() -> dict[str, object]:
    """Return the version, the selected implementations and the state of each
    component."""
    return build_health(NAME, VERSION)


@router.get("/agents")
def agents() -> dict[str, object]:
    """List the registered agents with their declared metadata."""
    return {
        "default": settings.default_agent,
        "agents": [
            AgentRegistry.get(name).metadata() for name in AgentRegistry.available()
        ],
    }


@router.post("/chat")
def chat(request: ChatRequest) -> ChatResponse:
    """Answer a question with the requested agent.

    Raises:
        HTTPException: 400 if the requested agent is not registered.
    """
    try:
        agent = AgentFactory.create(request.agent)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

    return ChatResponse(answer=agent.ask(request.message), agent=agent.name)
