from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field

from .envelope import ULID, Envelope


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid")


# ---------- Eventos cliente → servidor ----------


class FrameEvent(_Strict):
    """Etiqueta de un cuadro que viajó por el track de video. NO lleva la imagen."""

    t: Literal["frame"]
    frame_id: ULID
    """Asignado en el cliente al capturar. Llave de todo lo que refiera al cuadro."""
    ts: Annotated[int, Field(ge=0)]
    """Momento de captura; pegamento para correlacionar con el track."""
    blur_score: Annotated[float, Field(ge=0, le=1)]
    """0 = nítido, 1 = inservible. El cliente descarta bajo umbral antes de emitir."""


class CaptureAppliedEvent(_Strict):
    """Respuesta honesta a capture.policy: lo que se logró, no lo que se pidió."""

    t: Literal["capture.applied"]
    fps: Literal[1, 2, 4]
    max_edge: Literal[720, 1440]
    degraded_by: Literal["thermal", "bandwidth", "battery", "permission"] | None
    """Requerido; null = se cumplió tal cual."""


class FrameMissingEvent(_Strict):
    """El cliente ya no tiene el cuadro pedido en frame.pin (ring buffer de 90 s)."""

    t: Literal["frame.missing"]
    frame_id: ULID


class EquipmentManualEvent(_Strict):
    """Entrada manual del técnico. Lleva evidencia aunque la placa sea ilegible."""

    t: Literal["equipment.manual"]
    model: Annotated[str, Field(min_length=1)]
    serial: Annotated[str, Field(min_length=1)] | None
    evidence_frame_id: ULID


ClientPayload = Annotated[
    FrameEvent | CaptureAppliedEvent | FrameMissingEvent | EquipmentManualEvent,
    Field(discriminator="t"),
]

ClientEnvelope = Envelope[ClientPayload]
