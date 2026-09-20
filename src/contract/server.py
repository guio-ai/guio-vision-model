from typing import Annotated, Literal, Union

from pydantic import BaseModel, ConfigDict, Field

from .envelope import ULID, Envelope


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid")


# ---------- Tipos compartidos ----------

class CapturePolicy(_Strict):
    """Política de captura. Valores fijos: la restricción térmica vive en el tipo."""

    fps: Literal[1, 2, 4]
    """0.5 idle · 1 reposo · 2 trabajo · 4 solo ráfaga"""
    max_edge: Literal[720, 1440]
    """Lado largo en px. 1440 solo tiene sentido dentro de una ráfaga."""
    duration_ms: Annotated[int, Field(ge=500, le=15_000)] | None = None
    """Si viene, es ráfaga: el cliente revierte solo al expirar."""
    priority: Literal["required", "preferred"] = "preferred"
    """required = honrar aunque cueste térmicamente · preferred = degradar en silencio"""


# ---------- Eventos servidor → cliente ----------

class CapturePolicyEvent(_Strict):
    t: Literal["capture.policy"]
    policy: CapturePolicy
    reason: Literal["idle", "plate_detected", "retry", "manual"]


class FramePinEvent(_Strict):
    t: Literal["frame.pin"]
    frame_id: ULID
    reason: Literal["evidence", "retry"]


class EquipmentIdentifiedEvent(_Strict):
    t: Literal["equipment.identified"]
    model: Annotated[str, Field(min_length=1)]
    serial: Annotated[str, Field(min_length=1)] | None
    """Requerido pero puede ser null: a veces se lee el modelo y no la serie."""
    confidence: Annotated[float, Field(ge=0, le=1)]
    source: Literal["ocr", "manual"]
    evidence_frame_id: ULID


class ProcedureContext(_Strict):
    equipment_family: Annotated[str, Field(min_length=1)]
    complaint: Annotated[str, Field(min_length=1)]
    """Fijo en código en hito 1."""


class ProcedureSelectedEvent(_Strict):
    t: Literal["procedure.selected"]
    procedure_id: Annotated[str, Field(min_length=1)]
    title: Annotated[str, Field(min_length=1)]
    estimated_steps: Annotated[int, Field(gt=0)]
    """Estimados, no totales: con ramas no se sabe el total de antemano."""
    context: ProcedureContext


class AgentErrorEvent(_Strict):
    t: Literal["agent.error"]
    code: Literal["verify_inconclusive"]
    """En hito 2 se abre a un enum."""
    recoverable: Literal[True]
    user_message: Annotated[str, Field(min_length=1)]
    """Ya redactado por el servidor; el cliente lo muestra tal cual."""


# z.discriminatedUnion("t", [...])
ServerPayload = Annotated[
    Union[
        CapturePolicyEvent,
        FramePinEvent,
        EquipmentIdentifiedEvent,
        ProcedureSelectedEvent,
        AgentErrorEvent,
    ],
    Field(discriminator="t"),
]

ServerEnvelope = Envelope[ServerPayload]