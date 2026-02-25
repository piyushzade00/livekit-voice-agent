from livekit import api
import config

token = api.AccessToken(config.LIVEKIT_API_KEY, config.LIVEKIT_API_SECRET) \
    .with_identity("browser-user") \
    .with_name("browser-user") \
    .with_grants(api.VideoGrants(
        room_join=True,
        room=config.ROOM_NAME,
    )) \
    .to_jwt()

print("\nCopy this token into meet.livekit.io:\n")
print(token)