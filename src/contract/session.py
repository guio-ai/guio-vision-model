from typing import Annotated, Union

from pydantic import BaseModel, ConfigDict, Field, TypeAdapter

from .client import ClientPayload
from .envelope import UUID_STR, Envelope
from .server import ServerPayload

# Cualquier evento válido del hito 1, de cualquier lado.
# La unión de payloads sigue discriminada por "t", así que un evento con
# t="frame" solo intenta FrameEvent y el error apunta al campo real.
AnyPayload = Annotated[Union[ServerPayload, ClientPayload], Field(discriminator="t")]
AnyEnvelope = Envelope[AnyPayload]

_any_adapter = TypeAdapter(AnyEnvelope)


def parse_event(raw: bytes | str) -> AnyEnvelope:
    """Lo que hace el listener del agente al recibir bytes del canal de datos."""
    return _any_adapter.validate_json(raw)


class GoldenSession(BaseModel):
    """Forma del fixture golden_session.json"""

    model_config = ConfigDict(extra="forbid")

    session_id: UUID_STR
    note: str
    events: list[AnyEnvelope]