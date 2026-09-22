from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

# .ulid() de Zod → mismo regex estricto (Crockford base32, primer char 0-7)
ULID = Annotated[str, StringConstraints(pattern=r"^[0-7][0-9A-HJKMNP-TV-Z]{25}$")]
# .uuid() de Zod
UUID_STR = Annotated[
    str,
    StringConstraints(
        pattern=r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
    ),
]


class Envelope[P](BaseModel):
    """Sobre común a todos los eventos, en ambas direcciones.
    Lo único que varía es el tipo del payload, por eso es genérico.
    """

    # Zod rechaza claves desconocidas solo con .strict(); aquí las rechazamos
    # siempre para que un typo en un campo truene en vez de pasar en silencio.
    model_config = ConfigDict(extra="forbid")

    v: Literal[1]
    """Versión del contrato. Mismatch = fallar duro, no adivinar."""
    id: ULID
    """Identidad única del evento. Clave de idempotencia ante reintentos."""
    seq: Annotated[int, Field(gt=0)]
    """Monotónico por emisor y sesión. Un hueco = se perdió algo."""
    ts: Annotated[int, Field(ge=0)]
    """Epoch ms. El del cliente es advisory; el servidor lo corrige con offset."""
    session_id: UUID_STR
    """El id que devuelve POST /sessions."""
    causation_id: ULID | None = None
    """Evento que provocó este. Opcional en hito 1; obligatorio para confirm.ack en hito 2."""
    payload: P
