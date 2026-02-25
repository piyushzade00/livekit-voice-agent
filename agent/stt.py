import aiohttp
import io
import wave
import asyncio
import config


async def speech_to_text(audio_bytes):
    wav_buffer = io.BytesIO()
    with wave.open(wav_buffer, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(48000)
        wf.writeframes(audio_bytes)

    wav_buffer.seek(0)

    headers = {"authorization": config.ASSEMBLYAI_API_KEY}

    async with aiohttp.ClientSession() as session:

        async with session.post(
            "https://api.assemblyai.com/v2/upload",
            headers=headers,
            data=wav_buffer
        ) as r:
            upload = await r.json()
            if "upload_url" not in upload:
                return None
            audio_url = upload["upload_url"]

        async with session.post(
            "https://api.assemblyai.com/v2/transcript",
            json={
                "audio_url": audio_url,
                "speech_models": ["universal-2"]
            },
            headers=headers
        ) as r:
            transcript = await r.json()
            if "id" not in transcript:
                return None
            transcript_id = transcript["id"]

        while True:
            async with session.get(
                f"https://api.assemblyai.com/v2/transcript/{transcript_id}",
                headers=headers
            ) as r:
                result = await r.json()

                if result["status"] == "completed":
                    return result["text"]

                if result["status"] == "error":
                    return None

            await asyncio.sleep(1)