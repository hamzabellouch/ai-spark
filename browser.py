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

    def auto_detect_browser_on_port(self):
        """
        Attempts to detect which browser is listening on self.port.
        """
        try:
            output = self._check_output_text("netstat -ano")
            pid = None
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
        except Exception as e:
            print(f"Error auto-detecting browser on port {self.port}: {e}")
        return None

    def detect_running_browser(self):
        detected = self.auto_detect_browser_on_port()
        return detected if detected else self.browser_name

    def find_browser_executable(self):
        username = getpass.getuser()
        paths = []
        
        # If it is a direct path to an executable file
        if os.path.exists(self.browser_name) and self.browser_name.lower().endswith(".exe"):
            return self.browser_name
            
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
        
        for path in paths:
            if os.path.exists(path):
                return path
        return None

    def _get_pid_on_port(self):
        try:
            output = self._check_output_text("netstat -ano")
            for line in output.splitlines():
                if f"127.0.0.1:{self.port}" in line or f"[::1]:{self.port}" in line or f"0.0.0.0:{self.port}" in line:
                    parts = line.strip().split()
                    if len(parts) >= 5:
                        return parts[-1]
        except Exception as e:
            print(f"Error getting PID on port {self.port}: {e}")
        return None

    def get_default_user_data_dir(self):
        username = getpass.getuser()
        if self.browser_name == "chrome":
            return rf"C:\Users\{username}\AppData\Local\Google\Chrome\User Data"
        elif self.browser_name == "brave":
            return rf"C:\Users\{username}\AppData\Local\BraveSoftware\Brave-Browser\User Data"
        elif self.browser_name == "edge":
            return rf"C:\Users\{username}\AppData\Local\Microsoft\Edge\User Data"
        elif self.browser_name == "opera":
            return rf"C:\Users\{username}\AppData\Roaming\Opera Software\Opera Stable"
        return None

    async def launch_browser(self, force_kill=False):
        """
        Launches the browser with remote debugging enabled.
        For Firefox, we will launch it directly via Playwright's persistent context.
        For Chromium-based (chrome, edge, brave), we launch via subprocess with CDP flags.
        """
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
                        subprocess.run(["taskkill", "/F", "/PID", pid], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                        await asyncio.sleep(1.5)

        executable = self.find_browser_executable()
        if not executable and self.browser_name != "firefox":
            raise FileNotFoundError(f"Could not find executable for browser: {self.browser_name}")

        if self.browser_name != "firefox":
            if force_kill:
                print(f"Force-killing existing processes for {self.browser_name}...")
                exe_name = os.path.basename(executable)
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
            elif self.is_port_open():
                print(f"Browser is already running and listening on port {self.port}.")
                return True

        if self.browser_name == "firefox":
            return True

        # Always use an isolated workspace profile to ensure remote debugging port 9222 opens successfully,
        # avoids profile-picker disconnections, and prevents collision with already running browser windows.
        # Note: Recent Chrome versions (136+) explicitly block --remote-debugging-port on the default User Data directory.
        workspace_dir = os.path.dirname(os.path.abspath(__file__))
        clean_name = "".join([c if c.isalnum() else "_" for c in self.browser_name])
        profile_dir = os.path.join(workspace_dir, "profiles", clean_name)
        
        if not os.path.exists(profile_dir):
            default_dir = self.get_default_user_data_dir()
            if default_dir and os.path.exists(default_dir):
                print(f"Creating isolated profile by cloning default profile from {default_dir}...")
                import shutil
                import json
                try:
                    os.makedirs(profile_dir, exist_ok=True)
                    ls_path = os.path.join(default_dir, "Local State")
                    last_prof = "Default"
                    if os.path.exists(ls_path):
                        try:
                            with open(ls_path, "r", encoding="utf-8") as f:
                                ls_data = json.load(f)
                                last_prof = ls_data.get("profile", {}).get("last_used", "Default")
                            shutil.copy2(ls_path, os.path.join(profile_dir, "Local State"))
                        except Exception as e:
                            print(f"Error copying Local State: {e}")
                    
                    src_prof = os.path.join(default_dir, last_prof)
                    dst_prof = os.path.join(profile_dir, "Default")
                    if os.path.exists(src_prof):
                        print(f"Copying profile {last_prof} (excluding caches)... this may take a few seconds.")
                        shutil.copytree(src_prof, dst_prof, ignore=shutil.ignore_patterns('*Cache*', 'Code Cache', 'GPUCache', '*LOCK*'), dirs_exist_ok=True)
                        print("Profile cloned successfully.")
                except Exception as e:
                    print(f"Error during profile clone: {e}")

        os.makedirs(profile_dir, exist_ok=True)
        print(f"Using isolated workspace profile for {self.browser_name}: {profile_dir}")

        cmd = [
            executable,
            f"--remote-debugging-port={self.port}",
            f"--user-data-dir={profile_dir}",
            "--remote-allow-origins=*",
            "--no-first-run",
            "--no-default-browser-check"
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
                    workspace_dir = os.path.dirname(os.path.abspath(__file__))
                    profile_dir = os.path.join(workspace_dir, "profiles", "firefox")
                    os.makedirs(profile_dir, exist_ok=True)
                    executable = self.find_browser_executable()
                    launch_options = {
                        "user_data_dir": profile_dir,
                        "headless": False,
                        "args": ["--no-first-run"],
                        "viewport": {"width": 500, "height": 700}
                    }
                    if executable:
                        launch_options["executable_path"] = executable
                    
                    self.context = await self.playwright.firefox.launch_persistent_context(**launch_options)
                    self.browser = self.context.browser
                else:
                    self.browser = await self.playwright.chromium.connect_over_cdp(f"http://127.0.0.1:{self.port}", timeout=10000)
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

    async def close(self):
        if self.context and self.browser_name == "firefox":
            try:
                await self.context.close()
            except Exception as e:
                print(f"Error closing Firefox context: {e}")

        if self.browser:
            try:
                if self.browser_name == "firefox":
                    await self.browser.close()
                else:
                    await self.browser.disconnect()
            except Exception as e:
                print(f"Error closing/disconnecting: {e}")
            self.browser = None
            
        if self.playwright:
            try:
                await self.playwright.stop()
            except Exception as e:
                print(f"Error stopping playwright: {e}")
            self.playwright = None
            
        self.context = None
