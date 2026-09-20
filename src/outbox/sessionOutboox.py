from livekit.rtc.room import Room
import collections as col
from contract.envelope import Envelope
from contract.server import ServerPayload
import datetime

class SessionOutbox:
    def __init__(self, room: Room, session_id: str) -> None:
        self._room = room
        self._session_id = session_id
        self._seq = 0
        self._sent: col.deque[Envelope] = col.deque(maxlen=200)

    async def emit(self, payload: ServerPayload, causation_id: str | None = None) -> Envelope:
        self._seq += 1
        env = Envelope(
            v=1,
            id="1",
            seq=self._seq,
            ts=datetime.datetime.now().microsecond,
            session_id=self._session_id,
            payload=payload,
            **({"causation_id": causation_id} if causation_id else {})
        )
        raw = env.model_dump_json(exclude_unset=True)
        await self._room.local_participant.publish_data(raw.encode(), reliable=True)
        self._sent.append(env)
        return env
