from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.agents.registry import AgentRegistry
from app.api.health import build_health
from app.config import settings
from app.providers.registry import ProviderRegistry
from app.workspaces.manager import WorkspaceManager

NAME = "DevOps Mentor AI Platform"
VERSION = "1.0.0"
RELEASE_DATE = "2026-07-27"
API_V1_PREFIX = "/api/v1"

NOT_IMPLEMENTED_STATUS = 501

router = APIRouter()


class ChatRequest(BaseModel):
    """A question, answered in the workspace of a chat."""

    message: str
    agent: str = Field(
        default="",
        description=(
            "Agent for this request only, overriding the workspace without "
            "changing it. Empty uses the workspace agent."
        ),
    )
    chat_id: str = Field(
        default="",
        description="Whose workspace and history to use. Empty uses the default.",
    )


class ChatResponse(BaseModel):
    """The answer and the stack that produced it."""

    answer: str
    agent: str
    provider: str
    chat_id: str


class WorkspaceRequest(BaseModel):
    """A change to a workspace. Omitted fields stay as they are."""

    chat_id: str = ""
    user_id: str | None = None
    agent: str | None = None
    provider: str | None = None
    embedding: str | None = None
    memory: str | None = None
    retriever: str | None = None
    collection: str | None = None
    prompt: str | None = None


class WorkspaceResponse(BaseModel):
    """The result of a workspace change."""

    success: bool
    workspace: dict[str, str]


@router.get("/")
def root() -> dict[str, str]:
    """Return the name and the state of the service."""
    return {
        "name": NAME,
        "status": "running",
        "version": VERSION,
        "release_date": RELEASE_DATE,
    }


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


@router.get("/providers")
def providers() -> dict[str, object]:
    """List the registered providers with what each of them supports."""
    return {
        "default": settings.llm_provider,
        "providers": [
            ProviderRegistry.get(name).metadata()
            for name in ProviderRegistry.available()
        ],
    }


@router.get("/workspaces")
def workspaces() -> dict[str, object]:
    """List every workspace that has been used."""
    stored = WorkspaceManager.list()

    return {
        "count": len(stored),
        "workspaces": [workspace.as_dict() for workspace in stored],
    }


@router.get("/workspace")
def workspace(chat_id: str = "") -> dict[str, object]:
    """Return the workspace of a chat and what it resolves to."""
    return _workspace_document(chat_id)


@router.get("/workspace/{chat_id}")
def workspace_of(chat_id: str) -> dict[str, object]:
    """Return the workspace of a chat and what it resolves to."""
    return _workspace_document(chat_id)


@router.post("/workspace")
def update_workspace(request: WorkspaceRequest) -> WorkspaceResponse:
    """Change the stack of a chat. Every later message of that chat uses it.

    Raises:
        HTTPException: 400 if a name is not registered or not usable.
    """
    changes = request.model_dump(exclude={"chat_id"}, exclude_none=True)

    try:
        updated = WorkspaceManager.update(request.chat_id, **changes)
    except (ValueError, FileNotFoundError) as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

    return WorkspaceResponse(success=True, workspace=updated.as_dict())


@router.post("/chat")
def chat(request: ChatRequest) -> ChatResponse:
    """Answer a question in the workspace of the chat.

    Raises:
        HTTPException: 400 if the requested agent is not registered, 501 if the
            selected provider is registered but not implemented yet.
    """
    try:
        context = WorkspaceManager.resolve(request.chat_id, request.agent)
    except (ValueError, FileNotFoundError) as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

    try:
        answer = context.ask(request.message)
    except NotImplementedError as error:
        raise HTTPException(
            status_code=NOT_IMPLEMENTED_STATUS,
            detail=str(error),
        ) from error

    return ChatResponse(
        answer=answer,
        agent=context.agent.name,
        provider=context.runtime.selection["provider"],
        chat_id=context.workspace.chat_id,
    )


def _workspace_document(chat_id: str) -> dict[str, object]:
    """Return the stored names of a workspace and the stack they resolve to.

    Raises:
        HTTPException: 400 if the stored workspace cannot be resolved.
    """
    stored = WorkspaceManager.get(chat_id)

    try:
        resolved = WorkspaceManager.resolve(chat_id).describe()
    except (ValueError, FileNotFoundError) as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

    return {"workspace": stored.as_dict(), "resolved": resolved}
