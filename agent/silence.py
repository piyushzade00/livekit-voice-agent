import asyncio
import time
from agent.tts import speak_text


async def silence_monitor(agent):
    while True:
        await asyncio.sleep(2)

        if not agent.agent_speaking:
            elapsed = time.time() - agent.last_user_speech_time

            if elapsed > 20:
                agent.current_tts_task = asyncio.create_task(
                    speak_text(agent, "Are you still there?")
                )
                agent.last_user_speech_time = time.time()