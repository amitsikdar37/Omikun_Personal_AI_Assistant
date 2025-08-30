# Omikun_Personal_AI_Assistant
Our OMIKUN Personal AI Chat Assistant is still in building. If you want to use it clone it to your device and follow the ReadMe files steps to make it run properly on your device.


Here’s a complete README.md you can drop into the repository. It guides a new user from cloning to speaking with Omikun, supports both CPU and Ollama setups, and includes troubleshooting and memory/features notes. Citations are included for referenced behaviors, APIs, and practices.

# Omikun – Local Voice AI Assistant (Llama 3.1 8B + Faster-Whisper)

Omikun is a local, push-to-talk voice assistant that runs on a PC. Speak to transcribe with Faster-Whisper, think with Llama 3.1 8B via Ollama, and reply with offline TTS. It supports English and Hindi voice, keeps a short conversation history, and remembers durable facts (like name) across sessions.[1][2][3]

## Features
- Push-to-talk voice loop: hold Space to speak, release to process.[4]
- Local STT with Faster-Whisper (CTranslate2) for speed.[5]
- Local LLM via Ollama (llama3.1:8b) with multi-turn chat endpoint.[2][3]
- Offline TTS with pyttsx3; dynamic voice selection (English/Hindi).[6][7]
- Lightweight memory: short rolling history + persistent profile (e.g., name).[8][1]
- WhatsApp Web automation via Selenium (optional).[9]

## Requirements
- Windows 10/11 or macOS/Linux with Python 3.9+ installed.[10]
- For Windows: Visual Studio Build Tools only if compiling native packages, but most users won’t need this for Omikun’s default stack.[11]
- Chrome installed for WhatsApp Web automation (optional); Selenium 4 auto-manages the driver.[12]

## Quick Start (Recommended: Ollama + CPU)
1) Install Ollama and pull the model:
- Install Ollama (see ollama.dev), then:
- ollama pull llama3.1:8b
- This downloads and manages the model; runs as a background service on Windows listening on http://localhost:11434. No need to run “serve” manually.[13][2]

2) Clone the repo and enter it:
- git clone https://github.com/yourname/omikun.git
- cd omikun

3) Create and activate a virtual environment:
- Windows:
  - python -m venv omikun-env
  - omikun-env\Scripts\activate
- macOS/Linux:
  - python3 -m venv omikun-env
  - source omikun-env/bin/activate
Using a venv keeps dependencies isolated for the project.[14][10]

4) Install dependencies:
- pip install --upgrade pip
- pip install -r requirements.txt
If using requirements.txt from this repo, it includes Faster-Whisper, pyttsx3, sounddevice, Selenium, and requests.[5][6][9]

5) Run Omikun:
- python main.py
- Instructions appear in the console. Press and hold Space to talk; press Q to quit.[4]

## How It Works (Architecture)
- STT: Faster-Whisper transcribes audio to text locally with CTranslate2 optimizations.[5]
- LLM: The Ollama /api/chat endpoint receives a rolling message list (user/assistant) and an optional “system” prompt to steer behavior and inject memory. This improves multi-turn context and language control.[3][15][2]
- TTS: pyttsx3 uses the OS speech engine (SAPI5 on Windows) for offline speech. Voices can be selected by language or name (e.g., Hindi voices on Windows).[7][16][6]
- Memory: A small JSON file stores durable facts and a brief turn history; each turn sends a concise Memory summary via system prompt for consistent recall.[1][8]

## Repository Structure
- src/audio/stt.py — Faster-Whisper wrapper to transcribe audio.[5]
- src/audio/tts.py — pyttsx3-based TTS with per-call engine and language-aware voice pick.[6][7]
- src/llm/ollama_client.py — Chat client for Ollama’s /api/chat endpoint with rolling messages and optional system field.[2][3]
- src/agent/memory.py — Lightweight memory (profile.json + recent history).[1]
- src/tools/whatsapp_web.py — Selenium automation for WhatsApp Web (optional).[9]
- main.py — Push-to-talk loop, routing, and glue logic.[4]

## Keyboard Controls
- Space: Press and hold to record. Release to stop and process.[4]
- Q: Quit application gracefully.[4]

## Language Support (English + Hindi)
- STT detects the spoken language; Hindi is supported by Whisper models.[17]
- To speak in Hindi:
  - Ensure a Hindi TTS voice is installed in Windows (e.g., Hemant/Kalpana via Settings → Language & Region → Add language → Hindi with speech).[18]
  - The TTS automatically attempts to pick a Hindi voice if Devanagari characters are detected, or when instructed via lang hint.[16][7]
- The system prompt can encourage the LLM to reply in the same language as the user; the client passes a per‑turn system string through /api/chat.[15][3]

## WhatsApp Web (Optional)
- First run will prompt for a QR scan on web.whatsapp.com; Selenium 4 typically manages ChromeDriver automatically.[12][9]
- The example tool sets a Chrome user-data directory so the login persists between sessions.[9]
- Voice commands can be routed to tool actions (e.g., “Send a WhatsApp message to …”), but start by testing the function directly.[9]

## Troubleshooting

Ports and Ollama service
- Error: “bind: Only one usage of each socket address (port 11434) is permitted” → Ollama is already running as a service on Windows; do not call “ollama serve” manually. Test with: curl http://localhost:11434.[19][13]

Missing modules
- ModuleNotFoundError (e.g., selenium, keyboard): activate the venv and pip install the missing package or run pip install -r requirements.txt.[20][21]

Microphone issues / empty transcriptions
- Check Windows microphone privacy settings and device defaults; test recording independently. If audio arrays are silent, STT returns empty text. Use sounddevice with proper sample rate and ensure permissions are enabled.[22][23]

pyttsx3 only speaks once
- Re-initialize the engine each call (known workaround on Windows); avoid reusing the same engine instance in an event loop. This fixes “speaks only first time” behavior.[24][25]

Selenium driver errors
- Selenium 4 auto-manages drivers. If you still see “Unable to locate driver”, ensure Chrome is installed and up to date; Selenium will fetch the correct driver build.[26][12]

Windows PowerShell script activation
- If activate.ps1 is blocked, set execution policy for CurrentUser:
- Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
This allows venv activation scripts to run.[27][28]

## Developer Notes

Why /api/chat instead of /api/generate?
- /api/chat supports role-tagged multi‑turn conversations and aligns with Llama-3 chat templates. It also allows a system message per call for style, memory, and language instructions.[3][2]

Memory design
- A small JSON file stores durable facts (e.g., name) and a short history; each turn includes a compact “Memory:” in the system message. This pattern keeps latency low while maintaining consistent recall.[8][1]

Extending actions
- Add more tools (e.g., calendar, email) and a simple router: detect intents from text, invoke the tool, and send the result back to the LLM or TTS. Keep tools isolated and test independently.[29]

## Run Tests (Optional)
- python -m tests.test_imports
- python -m tests.test_tts
- python -m tests.test_microphone
- python -m tests.test_ollama
Running from the project root with -m ensures proper imports and resolves common “No module named src” errors.[30][31]

## Uninstall / Reset
- To remove the venv: deactivate then delete the omikun-env folder.[10]
- To reset memory, delete memory.json in the project root; Omikun will regenerate it.[1]

## License
Add your license here (e.g., MIT).

## Acknowledgements
- Faster-Whisper (CTranslate2) for fast local ASR.[5]
- Ollama for local LLM serving and chat API.[2][3]
- pyttsx3 for cross-platform offline TTS.[6]

## References
- Building local voice assistants and memory prompts.[1]
- Python event loop and keeping context concise.[8]
- Ollama /api/chat vs /api/generate and system prompting.[15][3][2]
- TTS voice selection and SAPI behavior on Windows.[7][16][6]
- Selenium 4 driver management basics.[12][9]

