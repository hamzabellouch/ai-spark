# AI Spark - macOS User Guide

## ⚡ How to Run

1. **Open Terminal** in this folder.
2. Make the script executable (only needed once):
   ```bash
   chmod +x run_macos.command
   ```
3. **Double-click `run_macos.command`** or run `./run_macos.command` in terminal to start the local backend server.
   - The script will automatically search for a working Python installation on your system (either `python3` or `python`), verify execution capability, and install dependencies from `src/requirements.txt`.
4. The program will automatically launch your **Brave browser** (or chosen browser) in debug mode and open `http://127.0.0.1:8000`.

---

## 🛠️ Diagnostics & Troubleshooting

If the application fails to launch:
1. Ensure **Python 3.11 or newer** is installed. You can install it via [python.org](https://www.python.org/) or Homebrew (`brew install python`).
2. If another application is running on port **8000**, close it or modify `src/main.py` and `run_macos.command` to use an alternative port.
3. If macOS blocks the script from running due to an unsigned developer warning:
   - Go to **System Settings > Privacy & Security**.
   - Scroll down to the Security section and click **Open Anyway** next to `run_macos.command`.
