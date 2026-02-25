import asyncio
import time
from livekit import api, rtc
import config

from agent.vad import AudioReceiver
from agent.stt import speech_to_text
from agent.tts import speak_text
from agent.silence import silence_monitor


class VoiceAgent:
    def __init__(self):
        self.room = rtc.Room()
        self.audio_source = None
        self.current_tts_task = None
        self.agent_speaking = False
        self.last_user_speech_time = time.time()

    async def start(self):
        token = api.AccessToken(
            config.LIVEKIT_API_KEY,
            config.LIVEKIT_API_SECRET
        ).with_identity(config.BOT_NAME) \
         .with_name(config.BOT_NAME) \
         .with_grants(api.VideoGrants(
             room_join=True,
             room=config.ROOM_NAME
         )).to_jwt()

        self.room.on("track_subscribed")(self.on_track_subscribed)

        await self.room.connect(config.LIVEKIT_URL, token)

        self.audio_source = rtc.AudioSource(48000, 1)
        track = rtc.LocalAudioTrack.create_audio_track(
            "bot-audio",
            self.audio_source
        )

        await self.room.local_participant.publish_track(track)

        print("Connected & bot track published.")

        asyncio.create_task(silence_monitor(self))

    def on_track_subscribed(self, track, publication, participant):
        if track.kind != rtc.TrackKind.KIND_AUDIO:
            return

        receiver = AudioReceiver(self, track)
        asyncio.create_task(receiver.run())

    async def handle_speech(self, audio_bytes):
        text = await speech_to_text(audio_bytes)
        if not text:
            return

        response = f"You said: {text}"

        self.current_tts_task = asyncio.create_task(
            speak_text(self, response)
        )