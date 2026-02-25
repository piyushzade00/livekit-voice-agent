import io
import asyncio
from gtts import gTTS
from pydub import AudioSegment
from livekit import rtc


async def text_to_pcm(text):
    tts = gTTS(text=text, lang='en')

    mp3_buffer = io.BytesIO()
    tts.write_to_fp(mp3_buffer)
    mp3_buffer.seek(0)

    audio = AudioSegment.from_file(mp3_buffer, format="mp3")
    audio = audio.set_frame_rate(48000).set_channels(1).set_sample_width(2)

    return audio.raw_data


async def speak_text(agent, text):
    agent.agent_speaking = True

    try:
        pcm = await text_to_pcm(text)
        frame_size = 960 * 2

        for i in range(0, len(pcm), frame_size):
            chunk = pcm[i:i + frame_size]

            if len(chunk) < frame_size:
                chunk += b"\x00" * (frame_size - len(chunk))

            frame = rtc.AudioFrame(
                data=chunk,
                sample_rate=48000,
                num_channels=1,
                samples_per_channel=960
            )

            await agent.audio_source.capture_frame(frame)
            await asyncio.sleep(0.02)

    except asyncio.CancelledError:
        pass

    finally:
        agent.agent_speaking = False