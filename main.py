import asyncio
from agent.voice_agent import VoiceAgent

async def main():
    agent = VoiceAgent()
    await agent.start()
    await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())