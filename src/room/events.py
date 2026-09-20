from livekit.rtc.participant import RemoteParticipant
from livekit.rtc.track import Track
from livekit.rtc.track_publication import RemoteTrackPublication
from livekit.rtc import VideoStream, TrackKind, VideoBufferType

def on_particpant_connected(participant: RemoteParticipant):
    print("Remote participant connected:", participant.name)

async def on_track_subscribed(track: Track, publication: RemoteTrackPublication, participant: RemoteParticipant):
    if track.kind == TrackKind.KIND_VIDEO:
        video_stream: VideoStream = VideoStream.from_track(track=track)
        
        async for frame in video_stream:
            print({
                "frame": frame.frame.__repr__(),
                "converted": frame.frame.convert(VideoBufferType.RGBA)
            })
        await video_stream.aclose()
    
    print({
        "track": {
            "name": track.name,
            "repr": track.__repr__()
        },
        "publication": {
            "name": publication.name,
            "repr": publication.__repr__()
        },
        "participant": {
            "name": participant.identity,
            "repr":  participant.__repr__()
        }
    })