import os
import subprocess
import socket
import asyncio
import getpass
from playwright.async_api import async_playwright

class BrowserController:
    def __init__(self, browser_name="brave", port=9222):
        self.browser_name = browser_name
        self.port = port
        self.playwright = None
        self.browser = None
        self.context = None
        self.process = None

    def _check_output_text(self, command):
        return subprocess.check_output(
            command,
            shell=True,
            text=True,
            encoding="utf-8",
            errors="ignore",
        )

    def is_connected(self):
        return self.browser is not None or self.context is not None

    def get_contexts(self):
        if self.browser:
            return self.browser.contexts
        if self.context:
            return [self.context]
        return []

    def is_port_open(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1.0)
            try:
                s.connect(('127.0.0.1', self.port))
                return True
            except (socket.error, socket.timeout):
                return False

    def is_browser_process_running(self):
        import sys
        executable = self.find_browser_executable()
        if not executable:
            exe_name = "firefox" if self.browser_name == "firefox" else self.browser_name
        else:
            exe_name = os.path.basename(executable)
            
        try:
            if sys.platform == "win32":
                output = self._check_output_text(f'tasklist /FI "IMAGENAME eq {exe_name}"')
                return exe_name.lower() in output.lower()
            else:
                output = subprocess.check_output(f'pgrep -f "{exe_name}"', shell=True, text=True)
                return bool(output.strip())
        except Exception:
            return False

    def auto_detect_browser_on_port(self):
        """
        Attempts to detect which browser is listening on self.port.
        """
        import sys
        try:
            pid = None
            if sys.platform == 'win32':
                output = self._check_output_text("netstat -ano")
                for line in output.splitlines():
                    if f"127.0.0.1:{self.port}" in line or f"[::1]:{self.port}" in line or f"0.0.0.0:{self.port}" in line:
                        parts = line.strip().split()
                        if len(parts) >= 5:
                            pid = parts[-1]
                            break
                if pid and pid != "0":
                    task_output = self._check_output_text(f'tasklist /FI "PID eq {pid}"')
                    task_output_lower = task_output.lower()
                    if "brave" in task_output_lower:
                        return "brave"
                    elif "chrome" in task_output_lower:
                        return "chrome"
                    elif "msedge" in task_output_lower:
                        return "edge"
                    elif "firefox" in task_output_lower:
                        return "firefox"
                    elif "opera" in task_output_lower:
                        return "opera"
                    else:
                        return "chrome"
            else:
                # macOS / Linux
                try:
                    pid = subprocess.check_output(f"lsof -t -i :{self.port}", shell=True, text=True).strip()
                    if pid:
                        pid = pid.split()[0]
                except Exception:
                    pass
                if pid:
                    task_output = subprocess.check_output(f"ps -p {pid} -o comm=", shell=True, text=True).strip().lower()
                    if "brave" in task_output:
                        return "brave"
                    elif "chrome" in task_output or "chromium" in task_output:
                        return "chrome"
                    elif "edge" in task_output:
                        return "edge"
                    elif "firefox" in task_output:
                        return "firefox"
                    elif "opera" in task_output:
                        return "opera"
        except Exception as e:
            print(f"Error auto-detecting browser on port {self.port}: {e}")
        return None

    def detect_running_browser(self):
        detected = self.auto_detect_browser_on_port()
        return detected if detected else self.browser_name

    def find_browser_executable(self):
        import sys
        import shutil
        username = getpass.getuser()
        
        # If it is a direct path to an executable file
        if os.path.exists(self.browser_name) and (self.browser_name.lower().endswith(".exe") or sys.platform != "win32"):
            if os.path.isfile(self.browser_name) and os.access(self.browser_name, os.X_OK):
                return self.browser_name
            
        # Attempt to use shutil.which (especially useful on Linux/macOS)
        exe_names = [self.browser_name]
        if self.browser_name == "chrome":
            exe_names = ["google-chrome", "google-chrome-stable", "chrome", "chromium", "chromium-browser"]
        elif self.browser_name == "brave":
            exe_names = ["brave-browser", "brave"]
        elif self.browser_name == "edge":
            exe_names = ["microsoft-edge", "microsoft-edge-stable", "edge"]
        elif self.browser_name == "opera":
            exe_names = ["opera", "opera-developer"]

        for name in exe_names:
            resolved = shutil.which(name)
            if resolved:
                return resolved

        paths = []
        if sys.platform == "win32":
            if self.browser_name == "chrome":
                paths = [
                    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                    rf"C:\Users\{username}\AppData\Local\Google\Chrome\Application\chrome.exe"
                ]
            elif self.browser_name == "edge":
                paths = [
                    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
                    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"
                ]
            elif self.browser_name == "brave":
                paths = [
                    r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
                    r"C:\Program Files (x86)\BraveSoftware\Brave-Browser\Application\brave.exe",
                    rf"C:\Users\{username}\AppData\Local\BraveSoftware\Brave-Browser\Application\brave.exe"
                ]
            elif self.browser_name == "firefox":
                paths = [
                    r"C:\Program Files\Mozilla Firefox\firefox.exe",
                    r"C:\Program Files (x86)\Mozilla Firefox\firefox.exe",
                    rf"C:\Users\{username}\AppData\Local\Mozilla Firefox\firefox.exe"
                ]
            elif self.browser_name == "opera":
                paths = [
                    r"C:\Program Files\Opera\launcher.exe",
                    r"C:\Program Files (x86)\Opera\launcher.exe",
                    rf"C:\Users\{username}\AppData\Local\Programs\Opera\launcher.exe",
                    rf"C:\Users\{username}\AppData\Local\Programs\Opera\opera.exe"
                ]
        elif sys.platform == "darwin":  # macOS
            if self.browser_name == "chrome":
                paths = ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"]
            elif self.browser_name == "brave":
                paths = ["/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"]
            elif self.browser_name == "edge":
                paths = ["/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"]
            elif self.browser_name == "firefox":
                paths = ["/Applications/Firefox.app/Contents/MacOS/firefox"]
            elif self.browser_name == "opera":
                paths = ["/Applications/Opera.app/Contents/MacOS/Opera"]
        else:  # Linux (if not in PATH)
            if self.browser_name == "chrome":
                paths = ["/usr/bin/google-chrome", "/usr/bin/google-chrome-stable", "/usr/bin/chromium", "/usr/bin/chromium-browser"]
            elif self.browser_name == "brave":
                paths = ["/usr/bin/brave-browser", "/usr/bin/brave"]
            elif self.browser_name == "edge":
                paths = ["/usr/bin/microsoft-edge", "/usr/bin/microsoft-edge-stable"]
            elif self.browser_name == "firefox":
                paths = ["/usr/bin/firefox"]
            elif self.browser_name == "opera":
                paths = ["/usr/bin/opera"]

        for path in paths:
            if os.path.exists(path):
                return path
        return None

    def _get_pid_on_port(self):
        import sys
        try:
            if sys.platform == 'win32':
                output = self._check_output_text("netstat -ano")
                for line in output.splitlines():
                    if f"127.0.0.1:{self.port}" in line or f"[::1]:{self.port}" in line or f"0.0.0.0:{self.port}" in line:
                        parts = line.strip().split()
                        if len(parts) >= 5:
                            return parts[-1]
            else:
                # Unix systems: use lsof or fuser
                try:
                    pid = subprocess.check_output(f"lsof -t -i :{self.port}", shell=True, text=True).strip()
                    if pid:
                        return pid.split()[0]
                except Exception:
                    pass
        except Exception as e:
            print(f"Error getting PID on port {self.port}: {e}")
        return None

    def get_default_user_data_dir(self):
        import os
        import sys
        import getpass
        username = getpass.getuser()
        
        # Determine clean browser name key (especially if custom executable path is provided)
        browser_key = self.browser_name.lower()
        if not browser_key.isalnum():
            base = os.path.basename(browser_key)
            if "chrome" in base:
                browser_key = "chrome"
            elif "brave" in base:
                browser_key = "brave"
            elif "edge" in base or "msedge" in base:
                browser_key = "edge"
            elif "opera" in base:
                browser_key = "opera"
            else:
                browser_key = "custom"
                
        if sys.platform == "win32":
            local_app_data = os.environ.get("LOCALAPPDATA", rf"C:\Users\{username}\AppData\Local")
            app_data = os.environ.get("APPDATA", rf"C:\Users\{username}\AppData\Roaming")
            if browser_key == "chrome":
                return os.path.join(local_app_data, "Google", "Chrome", "User Data")
            elif browser_key == "brave":
                return os.path.join(local_app_data, "BraveSoftware", "Brave-Browser", "User Data")
            elif browser_key == "edge":
                return os.path.join(local_app_data, "Microsoft", "Edge", "User Data")
            elif browser_key == "opera":
                path = os.path.join(app_data, "Opera Software", "Opera Stable")
                if not os.path.exists(path):
                    path = os.path.join(local_app_data, "Opera Software", "Opera Stable")
                return path
            elif browser_key == "custom":
                return os.path.join(local_app_data, "Google", "Chrome", "User Data")
        elif sys.platform == "darwin":  # macOS
            home = os.path.expanduser("~")
            if browser_key == "chrome":
                return os.path.join(home, "Library", "Application Support", "Google", "Chrome")
            elif browser_key == "brave":
                return os.path.join(home, "Library", "Application Support", "BraveSoftware", "Brave-Browser")
            elif browser_key == "edge":
                return os.path.join(home, "Library", "Application Support", "Microsoft Edge")
            elif browser_key == "opera":
                return os.path.join(home, "Library", "Application Support", "com.operasoftware.Opera")
            elif browser_key == "custom":
                return os.path.join(home, "Library", "Application Support", "Google", "Chrome")
        else:  # Linux
            home = os.path.expanduser("~")
            config = os.environ.get("XDG_CONFIG_HOME", os.path.join(home, ".config"))
            paths_to_check = []
            if browser_key == "chrome":
                paths_to_check = [
                    os.path.join(config, "google-chrome"),
                    os.path.join(home, ".var/app/com.google.Chrome/config/google-chrome"),
                    os.path.join(home, "snap/chromium/current/.config/chromium"),
                    os.path.join(home, "snap/chrome/current/.config/google-chrome")
                ]
            elif browser_key == "brave":
                paths_to_check = [
                    os.path.join(config, "BraveSoftware", "Brave-Browser"),
                    os.path.join(home, ".var/app/com.brave.Browser/config/BraveSoftware/Brave-Browser"),
                    os.path.join(home, "snap/brave/current/.config/BraveSoftware/Brave-Browser"),
                    os.path.join(home, "snap/brave-browser/current/.config/BraveSoftware/Brave-Browser")
                ]
            elif browser_key == "edge":
                paths_to_check = [
                    os.path.join(config, "microsoft-edge"),
                    os.path.join(home, ".var/app/com.microsoft.Edge/config/microsoft-edge")
                ]
            elif browser_key == "opera":
                paths_to_check = [
                    os.path.join(config, "opera"),
                    os.path.join(home, ".var/app/com.opera.Opera/config/opera")
                ]
            elif browser_key == "custom":
                paths_to_check = [
                    os.path.join(config, "google-chrome")
                ]
            
            for path in paths_to_check:
                if os.path.exists(path):
                    return path
            if paths_to_check:
                return paths_to_check[0]
            return os.path.join(config, browser_key)
                
        return None

    def get_firefox_default_profile_dir(self):
        dev_profile = os.path.abspath("firefox_dev_profile")
        os.makedirs(dev_profile, exist_ok=True)
        return dev_profile

    async def launch_browser(self, force_kill=False):
        """
        Launches the browser with remote debugging enabled.
        For Firefox, we will launch it directly via Playwright's persistent context.
        For Chromium-based (chrome, edge, brave), we launch via subprocess with CDP flags.
        """
        import sys
        # Auto-detect browser name before launching
        if self.is_port_open():
            detected = self.auto_detect_browser_on_port()
            if detected:
                if detected == self.browser_name and not force_kill:
                    print(f"Detected browser already running on port {self.port}: {self.browser_name}")
                    return True
                else:
                    print(f"Port {self.port} is occupied by {detected}. Terminating it to launch {self.browser_name}...")
                    pid = self._get_pid_on_port()
                    if pid and pid != "0":
                        if sys.platform == "win32":
                            subprocess.run(["taskkill", "/F", "/PID", pid], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                        else:
                            subprocess.run(["kill", "-9", pid], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                        await asyncio.sleep(1.5)

        executable = self.find_browser_executable()
        if not executable and self.browser_name != "firefox":
            raise FileNotFoundError(f"Could not find executable for browser: {self.browser_name}")

        if self.browser_name != "firefox":
            if force_kill:
                print(f"Force-killing existing processes for {self.browser_name}...")
                exe_name = os.path.basename(executable)
                if sys.platform == "win32":
                    subprocess.run(["taskkill", "/F", "/IM", exe_name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    # Wait up to 5 seconds for processes to fully exit and release profile locks
                    for _ in range(10):
                        try:
                            output = subprocess.check_output(f'tasklist /FI "IMAGENAME eq {exe_name}"', shell=True, text=True)
                            if "No tasks are running" in output or exe_name.lower() not in output.lower():
                                break
                        except Exception:
                            break
                        await asyncio.sleep(0.5)
                else:
                    # Unix systems (macOS/Linux)
                    subprocess.run(["pkill", "-f", exe_name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    subprocess.run(["killall", "-9", exe_name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    # Wait up to 5 seconds
                    for _ in range(10):
                        try:
                            output = subprocess.check_output(f'pgrep -f "{exe_name}"', shell=True, text=True)
                            if not output.strip():
                                break
                        except Exception:
                            break
                        await asyncio.sleep(0.5)
            elif self.is_port_open():
                print(f"Browser is already running and listening on port {self.port}.")
                return True
            elif self.is_browser_process_running():
                raise RuntimeError(
                    f"{self.browser_name.capitalize()} is already running but not in remote debugging mode (Port {self.port} is closed). "
                    "Please close the browser completely first, or restart it."
                )

        if self.browser_name == "firefox":
            if not force_kill and self.is_browser_process_running():
                raise RuntimeError(
                    "Firefox is already running. Please close the browser completely first, or restart it."
                )
            return True

        # Use the default User Data directory directly to leverage existing logins, cookies, and extensions
        profile_dir = self.get_default_user_data_dir()
        if not profile_dir or not os.path.exists(profile_dir):
            # Fallback to local profile directory for Linux/other support
            fallback_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), "profiles", f"linux_profile_{self.browser_name}"))
            print(f"Default user data directory not found or invalid. Using local profile directory for Linux support: {fallback_dir}")
            os.makedirs(fallback_dir, exist_ok=True)
            profile_dir = fallback_dir
        else:
            print(f"Using default User Data path: {profile_dir}")

        import sys
        null_device = "NUL" if sys.platform == "win32" else "/dev/null"

        cmd = [
            executable,
            f"--remote-debugging-port={self.port}",
            f"--user-data-dir={profile_dir}",
            "--remote-allow-origins=*",
            "--no-first-run",
            "--no-default-browser-check",
            "--disk-cache-size=1",
            "--media-cache-size=1",
            f"--disk-cache-dir={null_device}",
            "--disable-gpu-program-cache",
            "--disable-gpu-shader-disk-cache"
        ]

        print(f"Launching {self.browser_name} with command: {' '.join(cmd)}")
        self.process = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Wait for the port to open
        for _ in range(30):
            if self.is_port_open():
                print(f"Browser launched successfully on port {self.port}.")
                return True
            await asyncio.sleep(0.5)
            
        raise TimeoutError("Timed out waiting for browser to start on remote debugging port.")

    def _get_ws_url(self):
        import urllib.request
        import json
        
        # Try 127.0.0.1 first
        try:
            url = f"http://127.0.0.1:{self.port}/json/version"
            with urllib.request.urlopen(url, timeout=3) as response:
                data = json.loads(response.read().decode('utf-8'))
                return data.get("webSocketDebuggerUrl")
        except Exception as e:
            print(f"urllib failed to fetch from 127.0.0.1: {e}")
            
        # Fallback to localhost
        try:
            url = f"http://localhost:{self.port}/json/version"
            with urllib.request.urlopen(url, timeout=3) as response:
                data = json.loads(response.read().decode('utf-8'))
                return data.get("webSocketDebuggerUrl")
        except Exception as e:
            print(f"urllib failed to fetch from localhost: {e}")
            
        return None

    async def connect(self, retries=5, delay=2.0):
        """
        Connects Playwright to the launched browser.
        Retries multiple times in case the browser is currently restarting.
        """
        last_error = None
        for attempt in range(retries):
            try:
                # Clean up any existing connection first
                await self.close()
                
                self.playwright = await async_playwright().start()
                
                if self.browser_name == "firefox":
                    profile_dir = self.get_firefox_default_profile_dir()
                    print(f"Using Firefox profile: {profile_dir}")
                    executable = self.find_browser_executable()
                    launch_options = {
                        "user_data_dir": profile_dir,
                        "headless": False,
                        "args": ["--no-first-run"],
                        "viewport": {"width": 500, "height": 700},
                        "firefox_user_prefs": {
                            "browser.cache.disk.enable": False,
                            "browser.cache.memory.enable": True,
                            "browser.cache.offline.enable": False,
                            "network.http.use-cache": False
                        }
                    }
                    if executable:
                        launch_options["executable_path"] = executable
                    
                    self.context = await self.playwright.firefox.launch_persistent_context(**launch_options)
                    self.browser = self.context.browser
                else:
                    # Set proxy bypass variables for loopback connections
                    import os
                    os.environ["NO_PROXY"] = "127.0.0.1,localhost"
                    os.environ["no_proxy"] = "127.0.0.1,localhost"
                    
                    # Fetch WebSocket URL directly using Python urllib to bypass Node.js HTTP ECONNRESET issues
                    ws_url = None
                    try:
                        ws_url = self._get_ws_url()
                    except Exception as ws_err:
                        print(f"Error fetching WS URL: {ws_err}")

                    if ws_url:
                        print(f"Connecting to browser via direct WebSocket: {ws_url}")
                        try:
                            self.browser = await self.playwright.chromium.connect_over_cdp(
                                ws_url,
                                timeout=5000,
                                no_defaults=True
                            )
                        except TypeError:
                            self.browser = await self.playwright.chromium.connect_over_cdp(
                                ws_url,
                                timeout=5000
                            )
                    else:
                        # Fallback to HTTP URL connection
                        print("Fallback to HTTP connection...")
                        try:
                            # Try 127.0.0.1 first
                            try:
                                self.browser = await self.playwright.chromium.connect_over_cdp(
                                    f"http://127.0.0.1:{self.port}",
                                    timeout=5000,
                                    no_defaults=True
                                )
                            except TypeError:
                                self.browser = await self.playwright.chromium.connect_over_cdp(
                                    f"http://127.0.0.1:{self.port}",
                                    timeout=5000
                                )
                        except Exception as first_err:
                            print(f"CDP connection to 127.0.0.1 failed ({first_err}). Trying localhost fallback...")
                            # Fallback to localhost (resolves to IPv6 [::1] or IPv4 depending on OS configuration)
                            try:
                                self.browser = await self.playwright.chromium.connect_over_cdp(
                                    f"http://localhost:{self.port}",
                                    timeout=5000,
                                    no_defaults=True
                                )
                            except TypeError:
                                self.browser = await self.playwright.chromium.connect_over_cdp(
                                    f"http://localhost:{self.port}",
                                    timeout=5000
                                )
                    self.context = self.browser.contexts[0]

                print(f"Playwright successfully connected to {self.browser_name}.")
                return self.context
            except Exception as e:
                last_error = e
                print(f"Connect attempt {attempt + 1} failed: {e}. Retrying in {delay}s...")
                await asyncio.sleep(delay)
                
        raise last_error or Exception("Failed to connect to the browser after multiple attempts.")

    async def await_profile_selection(self, timeout=60):
        """
        Waits for the user to select a profile from the profile picker.
        We know they selected a profile when we see a page that is a normal webpage or newtab.
        """
        if self.browser_name == "firefox":
            return None
            
        print("Waiting for profile selection...")
        start_time = asyncio.get_event_loop().time()
        last_debug_time = 0.0
        
        while asyncio.get_event_loop().time() - start_time < timeout:
            current_time = asyncio.get_event_loop().time()
            if current_time - last_debug_time > 5.0:
                print("Checking for active profile selection...")
                last_debug_time = current_time
                
            try:
                pages = self.get_pages()
                
                # Reconnect if there are no pages (e.g., profile picker closed and window transitioning)
                if not pages:
                    print("No pages detected. Reconnecting to find new profile window...")
                    await self.connect()
                    await asyncio.sleep(1.0)
                    continue
                    
                for page in pages:
                    try:
                        url = page.url.lower().strip()
                        is_normal = (
                            url.startswith("http://") or 
                            url.startswith("https://") or 
                            url.startswith("chrome://") or
                            url.startswith("brave://") or
                            url == "about:blank" or 
                            "newtab" in url or 
                            "new-tab" in url or 
                            "startpage" in url
                        )
                        is_picker = "profile-picker" in url or "chrome-signin" in url
                        
                        if is_normal and not is_picker:
                            print(f"Profile selected! Detected page: {url}")
                            return page
                    except Exception:
                        continue
            except Exception as e:
                print(f"Connection issue during profile selection ({e}). Reconnecting...")
                try:
                    await self.connect()
                except Exception as ce:
                    print(f"Reconnect failed: {ce}")
            await asyncio.sleep(0.5)
            
        print("Timed out waiting for profile selection.")
        return None

    def get_pages(self):
        if not self.is_connected():
            raise Exception("Browser not connected. Call connect() first.")
        pages = []
        for context in self.get_contexts():
            try:
                pages.extend(context.pages)
            except Exception as e:
                print(f"Error getting pages from context: {e}")
        return pages

    def get_active_context(self):
        if not self.is_connected():
            raise Exception("Browser not connected. Call connect() first.")
        
        # Check contexts from newest to oldest
        contexts = self.get_contexts()
        for context in reversed(contexts):
            for page in context.pages:
                try:
                    url = page.url.lower()
                    # If we find a page that is a normal website, this is the active context
                    if "profile-picker" not in url and "chrome-signin" not in url:
                        return context
                except:
                    continue
                    
        # Fallback to the last context or the first context
        return contexts[-1] if contexts else self.context

    async def find_tab(self, keyword):
        if not self.is_connected():
            raise Exception("Browser not connected. Call connect() first.")
        
        for context in self.get_contexts():
            for page in context.pages:
                try:
                    title = (await page.title()).lower()
                    url = page.url.lower()
                    if keyword.lower() in title or keyword.lower() in url:
                        return page
                except Exception as e:
                    print(f"Error reading page info: {e}")
                    continue
        return None

    async def open_or_get_tab(self, keyword, url):
        """
        Gets the tab if already open, or opens a new tab navigating to the URL.
        """
        try:
            page = await self.find_tab(keyword)
            if page:
                try:
                    await page.bring_to_front()
                    return page
                except Exception as e:
                    print(f"Error bringing tab '{keyword}' to front: {e}. Opening new tab...")
            
            print(f"Tab for '{keyword}' not found. Opening a new tab for {url}...")
            context = self.get_active_context()
            page = await context.new_page()
            
            # Load in background to allow concurrent loading and add retry logic
            async def load_with_retry():
                for attempt in range(3):
                    try:
                        await page.goto(url, timeout=45000)
                        return  # Success
                    except Exception as e:
                        print(f"Error loading {url} (attempt {attempt+1}/3): {e}")
                        if attempt < 2:
                            await asyncio.sleep(2)
                            
            asyncio.create_task(load_with_retry())
            await asyncio.sleep(0.2)  # Give it a tiny moment to start navigation
            
            return page
        except Exception as e:
            print(f"Error in open_or_get_tab for '{keyword}': {e}. Retrying with fresh connection in 2s...")
            await asyncio.sleep(2.0)
            try:
                await self.connect(retries=3, delay=2.0)
                context = self.get_active_context()
                page = await context.new_page()
                
                async def load_with_retry_fallback():
                    for attempt in range(3):
                        try:
                            await page.goto(url, timeout=45000)
                            return
                        except Exception as e:
                            if attempt < 2:
                                await asyncio.sleep(2)
                                
                asyncio.create_task(load_with_retry_fallback())
                await asyncio.sleep(0.2)
                
                return page
            except Exception as retry_err:
                print(f"Retry in open_or_get_tab failed: {retry_err}")
                raise retry_err

    async def close(self, terminate_process=False):
        if self.context and self.browser_name == "firefox":
            try:
                await self.context.close()
            except Exception as e:
                print(f"Error closing Firefox context: {e}")

        if self.browser:
            try:
                await self.browser.close()
            except Exception as e:
                print(f"Error closing browser: {e}")
            self.browser = None
            
        if self.playwright:
            try:
                await self.playwright.stop()
            except Exception as e:
                print(f"Error stopping playwright: {e}")
            self.playwright = None
            
        if terminate_process and self.process:
            try:
                self.process.terminate()
                for _ in range(20):
                    if self.process.poll() is not None:
                        break
                    await asyncio.sleep(0.1)
                if self.process.poll() is None:
                    self.process.kill()
            except Exception as e:
                print(f"Error terminating browser process: {e}")
            self.process = None
            
        self.context = None
