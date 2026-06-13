# AI Spark - Windows User Guide

AI Spark (formerly Broadcast AI Hub) is a local FastAPI web interface that allows you to simultaneously broadcast a query to multiple AI chat interfaces (ChatGPT, Gemini, DeepSeek) running inside your web browser (Brave, Chrome, Edge), view and compare their results side-by-side in a beautiful grid layout, and generate a unified synthesized response via Claude.

---

## ⚡ Quick Start

1. **Double-click `run_windows.bat`** to start the local backend server.
   - The script will automatically search for a working Python installation on your system (either through the Python launcher `py` or the direct command `python`), verify execution capability, and install dependencies from `requirements.txt`.
2. The program will automatically launch your **Brave browser** in debug mode and open `http://127.0.0.1:8000`.
   - If Brave is already running, please close all its windows first so the application can launch it with remote debugging enabled (`--remote-debugging-port=9222`).

---

## 🎨 Key Features

- **Splash Screen Loader:** Features an elegant 3-second animated splash loader upon loading the page.
- **Side-by-Side Comparison Grid:** Compare responses from ChatGPT, Gemini, and DeepSeek in a responsive grid layout.
- **Claude Synthesis Highlight:** Highlights the unified synthesized response from Claude with Anthropic's theme styling.
- **Dynamic Interface:** Supports light and dark modes, RTL/LTR layouts for multi-language usage, and an integrated session history.

---

## 🛠️ Diagnostics & Troubleshooting

If the application exits immediately or fails to launch:
1. Ensure **Python 3.11 or newer** is installed from [python.org](https://www.python.org/) and the option **"Add python.exe to PATH"** was checked during installation.
2. If another application is running on port **8000**, close it or modify `main.py` and `run_windows.bat` to use an alternative port.
3. Open a command prompt (`cmd`) in this folder, and run:
   ```cmd
   run_windows.bat
   ```
   This will keep the window open so you can view any specific error messages or log tracebacks.
