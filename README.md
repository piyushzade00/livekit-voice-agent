---

#️ Real-Time Voice Agent (LiveKit)

A real-time voice agent built using **LiveKit (Python SDK)** that joins a room, listens to user speech, converts it to text, responds with `"You said: <text>"`, and plays the response back via audio.

The agent supports:

* Speech-to-Text (STT)
* Text-to-Speech (TTS)
* Voice Activity Detection (VAD)
* Immediate interruption (No Overlap)
* Silence reminder after 20 seconds

---

# Features

## Option B Implementation (STT → Response → TTS)

* Captures live audio from LiveKit room
* Converts speech to text using AssemblyAI
* Generates response: `"You said: <text>"`
* Converts response to speech using gTTS
* Streams audio back in real time

---

## No Overlap Handling (Required)

The agent:

* Detects user speech using RMS-based Voice Activity Detection (VAD)
* Immediately cancels bot speech if the user starts speaking
* Uses async task cancellation for real-time interruption
* Maintains speaking-state flags to prevent overlap

---

## Silence Handling (Required)

* Tracks last detected user speech

* If no speech for 20+ seconds → plays reminder:

  "Are you still there?"

* Does not continuously loop or spam audio

* Uses background async silence monitor task

---

# Project Structure

```
voice-agent-python/
│
├── main.py
├── config.example.py
│
├── agent/
│   ├── __init__.py
│   ├── voice_agent.py
│   ├── vad.py
│   ├── stt.py
│   ├── tts.py
│   └── silence.py
```

### Architecture Overview

* `voice_agent.py` → Core orchestration
* `vad.py` → Audio receiving & voice detection
* `stt.py` → AssemblyAI integration
* `tts.py` → TTS generation & audio streaming
* `silence.py` → Silence monitoring logic

The design is modular and event-driven using `asyncio`.

---

# SDK Used

* **LiveKit Python SDK**
* AsyncIO (Python built-in)
* NumPy (RMS energy calculation)

---

# External Services Used

| Service        | Purpose              |
| -------------- | -------------------- |
| LiveKit Cloud  | Real-time audio room |
| AssemblyAI API | Speech-to-Text       |
| gTTS           | Text-to-Speech       |

---

# Setup Instructions

## 1️⃣ Clone Repository

```bash
git clone <your-repo-url>
cd voice-agent-python
```

---

## 2️⃣ Create Virtual Environment

```bash
python -m venv venv
```

Activate:

Windows:

```bash
venv\Scripts\activate
```

Mac/Linux:

```bash
source venv/bin/activate
```

---

## 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

If `requirements.txt` is not present:

```bash
pip install livekit aiohttp numpy gTTS pydub
```

---

## 4️⃣ Install FFmpeg (Required for TTS)

### Windows:

Download from:
[https://ffmpeg.org/download.html](https://ffmpeg.org/download.html)

Add `ffmpeg/bin` to system PATH.

Verify:

```bash
ffmpeg -version
```

---

# Required Environment Variables

🔑 Configuration

## 1️⃣  Copy the example configuration file:

copy config.example.py config.py   # Windows

or

cp config.example.py config.py     # Mac/Linux

## 2️⃣   Open config.py and fill in your credentials.
```

---

# How To Run

Start the agent:

```bash
python main.py
```

Then:

1. Join the same LiveKit room from browser
2. Speak into microphone
3. Agent will respond:

   ```
   You said: <your speech>
   ```

---

# Technical Design Decisions

### 1️⃣ Voice Activity Detection

* RMS energy-based detection
* Frame smoothing using consecutive speech frames
* Silence window of 800ms before ending segment

### 2️⃣ No Overlap Handling

* Maintains `agent_speaking` state
* Cancels TTS async task on user speech
* Prevents simultaneous speaking

### 3️⃣ Real-Time Audio Streaming

* 20ms frame chunks
* Proper 48kHz mono 16-bit PCM format
* Silence padding for final chunk

---

# Known Limitations

* RMS-based VAD (not ML-based)
* Uses non-streaming STT (AssemblyAI polling)
* Uses non-streaming TTS (gTTS) → 1–2s latency
* Network latency depends on external APIs
* Designed for demonstration and evaluation purposes. Not production-optimized.

---

# Assignment Evaluation Alignment

* This implementation focuses on:
* Real-time audio streaming using 20ms frame chunks
* Strict speaking-state management to prevent overlap
* Immediate interruption using async task cancellation
* Modular architecture with clear separation of concerns
* Explicit silence detection logic (20-second inactivity rule)