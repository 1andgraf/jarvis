# Jarvis - AI Helper Desktop App

## Overview
Jarvis is a multi-functional AI-powered desktop assistant built with Python using CustomTkinter and pytgpt. The app provides AI chat, notes management, weather information, timers, app shortcuts, and system monitoring functionalities, all in a clean and modern GUI.

---

## Features

### 1. AI Chat
- Ask questions or have a conversation with the AI.
- Supports commands like `open <app>` and `search <query>`.
- Uses the Phind API via `pytgpt.phind`.

### 2. Notes
- Create, edit, and delete notes.
- Click on a note to edit instantly.
- Notes have a delete button for quick removal.

### 3. Weather
- Enter a city name to get current weather conditions.
- Displays city, country, temperature, and weather conditions.
- Uses the Open-Meteo API.

### 4. Timer
- Create multiple timers with hours, minutes, and seconds.
- Timers display in the main field above the input.
- Start and run multiple timers simultaneously.

### 5. App Shortcuts
- Add custom shortcuts with a name and path.
- Shortcuts appear in the main field for easy access.
- Launch apps directly from the app.

### 6. System Monitor
- Monitor CPU, GPU, RAM, and SSD usage.
- Shows current usage percentage and temperatures.
- On Windows, supports CPU fan RPM monitoring (requires OpenHardwareMonitorLib).
- Provides a button to open Task Manager (Windows) or Activity Monitor (macOS).

---

## Installation

### Requirements
- Python 3.11+
- Packages:
  - `customtkinter`
  - `pytgpt`
  - `requests`
  - `psutil`
  - `GPUtil` (optional for GPU monitoring)

Install dependencies:
```bash
pip install customtkinter pytgpt requests psutil GPUtil
```

### Running Locally
```bash
python jarvis.py
```

### Building Executable (Windows)
```bash
pip install pyinstaller
pyinstaller --windowed --name Jarvis jarvis.py
```
- The executable will be in `dist/Jarvis/`.
- Use `--onefile` to create a single `.exe` file (slower startup).

### Building macOS App
```bash
pip install pyinstaller
pyinstaller --windowed --name Jarvis jarvis.py
```
- The `.app` will be in `dist/Jarvis/`.
- For icons or resources, include them with `--add-data`.

---

## Usage
1. Launch Jarvis.
2. Use the top menu to switch between modes (AI Chat, Weather, Timer, Notes, Apps, System Monitor).
3. Interact with the input boxes and buttons in each mode.
4. On Windows, CPU fan RPM monitoring is available in System Monitor (requires OpenHardwareMonitorLib.dll).

---

## Notes
- The application is fully cross-platform, but some features like CPU fan RPM control are Windows-only.
- macOS and Linux versions will disable Windows-specific features gracefully.
- Startup may be slower if packaged with `--onefile` due to extraction.

---

## License
MIT License