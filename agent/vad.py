import numpy as np
import asyncio
import time
from livekit import rtc


class AudioReceiver:
    def __init__(self, agent, track):
        self.agent = agent
        self.track = track
        self.threshold = 300
        self.required_frames = 5
        self.silence_ms = 800

    async def run(self):
        stream = rtc.AudioStream(self.track)

        speaking = False
        silence_start = None
        speech_frames = 0
        buffer = bytearray()

        async for event in stream:
            pcm = event.frame.data

            audio_np = np.frombuffer(pcm, dtype=np.int16).astype(np.float32)
            rms = np.sqrt(np.mean(audio_np ** 2))

            now = time.time()

            if rms > self.threshold:
                speech_frames += 1

                if not speaking and speech_frames >= self.required_frames:
                    speaking = True
                    self.agent.last_user_speech_time = time.time()

                    if self.agent.agent_speaking and self.agent.current_tts_task:
                        self.agent.current_tts_task.cancel()

                if speaking:
                    buffer.extend(pcm)

                silence_start = None

            else:
                speech_frames = 0
                if speaking:
                    if silence_start is None:
                        silence_start = now
                    elif (now - silence_start) * 1000 > self.silence_ms:
                        speaking = False
                        captured = bytes(buffer)
                        buffer.clear()
                        asyncio.create_task(
                            self.agent.handle_speech(captured)
                        )
                        silence_start = None