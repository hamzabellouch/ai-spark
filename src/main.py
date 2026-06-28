print("Backend: Starting main.py...")
import os
import sys
import asyncio
import warnings

# Suppress event loop policy deprecation warning on Windows startup
warnings.filterwarnings("ignore", category=DeprecationWarning)

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
from fastapi import FastAPI, HTTPException, Body, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from browser import BrowserController
from agents import AIAgents
from utils import wait_for_response_to_finish
from claude_synth import ClaudeSynthesizer
import db

from contextlib import asynccontextmanager

async def auto_launch_browser():
    global browser_ctrl, current_browser_name
    await asyncio.sleep(1.5)  # wait for uvicorn to fully start
    print(f"Auto-launching {current_browser_name.capitalize() if not os.path.isabs(current_browser_name) else 'Custom Browser'} in debug mode...")
    try:
        if not browser_ctrl:
            browser_ctrl = BrowserController(browser_name=current_browser_name)
        
        # Check if the browser is running but the port is closed (or Firefox is running)
        is_running_no_debug = False
        if current_browser_name == "firefox":
            if browser_ctrl.is_browser_process_running():
                is_running_no_debug = True
        else:
            if browser_ctrl.is_browser_process_running() and not browser_ctrl.is_port_open():
                is_running_no_debug = True

        if is_running_no_debug:
            loop = asyncio.get_event_loop()
            ans = await loop.run_in_executor(
                None,
                lambda: input(f"Error auto launch browser (do you want to restart {current_browser_name.capitalize() if not os.path.isabs(current_browser_name) else 'browser'}? y/n): ").strip().lower()
            )
            if ans in ('y', 'yes'):
                print(f"Restarting {current_browser_name.capitalize() if not os.path.isabs(current_browser_name) else 'browser'}...")
                await browser_ctrl.launch_browser(force_kill=True)
            else:
                print("Browser restart declined. Skipping auto-launch.")
                return
        else:
            await browser_ctrl.launch_browser(force_kill=False)

        if not browser_ctrl.is_connected():
            await browser_ctrl.connect()
        await browser_ctrl.await_profile_selection()
        
        # Open essential AI pages automatically on startup
        urls = {
            "chatgpt": "https://chatgpt.com",
            "gemini": "https://gemini.google.com",
            "deepseek": "https://chat.deepseek.com",
            "claude": "https://claude.ai"
        }
        for keyword, url in urls.items():
            await browser_ctrl.open_or_get_tab(keyword, url)
            await asyncio.sleep(0.5)
            
        await browser_ctrl.open_or_get_tab("spark", "http://127.0.0.1:8000")
        print("Dashboard and AI tabs opened successfully.")
    except Exception as e:
        print(f"Error auto-launching browser: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("==================================================================")
    print(" AI Spark server started successfully! ")
    print(f" Launching {current_browser_name.capitalize() if not os.path.isabs(current_browser_name) else 'Custom Browser'} automatically... ")
    print("==================================================================")
    db.init_db()
    asyncio.create_task(auto_launch_browser())
    yield
    global browser_ctrl
    if browser_ctrl:
        await browser_ctrl.close(terminate_process=True)
        browser_ctrl = None

app = FastAPI(title="AI Spark", lifespan=lifespan)
# Global variables to store browser state and configuration
browser_ctrl = None
current_browser_name = "brave"

class LaunchPayload(BaseModel):
    force_kill: bool = False

class FilePayload(BaseModel):
    name: str
    mime_type: str
    data: str

class QueryPayload(BaseModel):
    question: str
    agents: list[str] = Field(default_factory=lambda: ["chatgpt", "gemini", "deepseek"])
    synthesize: bool = True
    files: list[FilePayload] = Field(default_factory=list)

# Mount static directory for CSS/JS
os.makedirs("static", exist_ok=True)
os.makedirs("templates", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def get_index():
    index_path = "templates/index.html"
    if not os.path.exists(index_path):
        raise HTTPException(status_code=404, detail="Frontend index.html not found.")
    with open(index_path, "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

@app.get("/favicon.ico")
async def favicon():
    if os.path.exists("static/favicon.ico"):
        return FileResponse("static/favicon.ico")
    elif os.path.exists("static/icons/lightning.svg"):
        return FileResponse("static/icons/lightning.svg", media_type="image/svg+xml")
    return HTMLResponse(status_code=204)



@app.get("/api/status")
async def get_status():
    global browser_ctrl, current_browser_name
    
    if not browser_ctrl:
        browser_ctrl = BrowserController(browser_name=current_browser_name)
        
    # Auto-detect browser name based on netstat (if port is open) or tasklist (if port is closed)
    if browser_ctrl.is_port_open():
        detected = browser_ctrl.auto_detect_browser_on_port()
        if detected:
            browser_ctrl.browser_name = detected
            current_browser_name = detected
            
        # Auto-connect if the port is open and we aren't connected yet
        if not browser_ctrl.is_connected():
            try:
                print(f"Browser debugging port is open ({browser_ctrl.browser_name}). Attempting automatic connection...")
                await browser_ctrl.connect()
            except Exception as e:
                print(f"Auto-connection to browser failed: {e}")
    if not browser_ctrl.is_connected():
        return {
            "connected": False,
            "browser": current_browser_name,
            "tabs": {
                "chatgpt": False,
                "gemini": False,
                "deepseek": False,
                "claude": False
            }
        }
        
    try:
        # Check if browser is still responsive by fetching pages
        pages = browser_ctrl.get_pages()
        
        chatgpt_tab, gemini_tab, deepseek_tab, claude_tab = await asyncio.gather(
            browser_ctrl.find_tab("chatgpt"),
            browser_ctrl.find_tab("gemini"),
            browser_ctrl.find_tab("deepseek"),
            browser_ctrl.find_tab("claude"),
        )
        tab_status = {
            "chatgpt": chatgpt_tab is not None,
            "gemini": gemini_tab is not None,
            "deepseek": deepseek_tab is not None,
            "claude": claude_tab is not None
        }
        
        return {
            "connected": True,
            "browser": current_browser_name,
            "tabs": tab_status
        }
    except Exception as e:
        print(f"Status check failed: {e}. Disconnecting browser controller.")
        try:
            await browser_ctrl.close()
        except:
            pass
        browser_ctrl = None
        return {
            "connected": False,
            "browser": current_browser_name,
            "tabs": {
                "chatgpt": False,
                "gemini": False,
                "deepseek": False,
                "claude": False
            }
        }

@app.post("/api/browser/launch")
async def launch_browser_tabs(request: Request, payload: LaunchPayload = Body(default=LaunchPayload())):
    global browser_ctrl, current_browser_name
    
    try:
        if not browser_ctrl:
            browser_ctrl = BrowserController(browser_name=current_browser_name)
            
        await browser_ctrl.launch_browser(payload.force_kill)
        current_browser_name = browser_ctrl.browser_name
        
        # Verify connection is responsive, reconnect if not
        is_responsive = False
        if browser_ctrl.is_connected():
            try:
                browser_ctrl.get_pages()
                is_responsive = True
            except Exception as e:
                print(f"Stale connection detected during launch: {e}. Reconnecting...")
                try:
                    await browser_ctrl.close()
                except:
                    pass
                
        if not browser_ctrl.is_connected():
            await browser_ctrl.connect()
        
        # Wait for user to select a profile if profile picker is displayed
        await browser_ctrl.await_profile_selection()
        
        # Open essential AI pages
        urls = {
            "chatgpt": "https://chatgpt.com",
            "gemini": "https://gemini.google.com",
            "deepseek": "https://chat.deepseek.com",
            "claude": "https://claude.ai"
        }
        
        # Open tabs in sequence
        for keyword, url in urls.items():
            await browser_ctrl.open_or_get_tab(keyword, url)
            await asyncio.sleep(0.5)
            
        # Bring the program's dashboard tab back to focus so the user returns to the control panel
        await browser_ctrl.open_or_get_tab("spark", "http://127.0.0.1:8000")
        return {"status": "success", "message": f"{current_browser_name.capitalize() if not os.path.isabs(current_browser_name) else 'Browser'} launched with AI tabs."}
        
    except Exception as e:
        browser_ctrl = None
        error_msg = (
            f"Could not launch or connect to the browser. Please check the following:\n"
            f"1. Ensure all open windows of {current_browser_name.capitalize() if not os.path.isabs(current_browser_name) else 'browser'} are fully closed (from Task Manager if needed) so the program can release the lock and control your default profile.\n"
            f"2. If you are using Google Chrome (version 136+), Google blocks remote control of the default profile for security reasons. We recommend using an alternative browser like Brave, Edge, or Firefox.\n"
            f"Error details: {e}"
        )
        raise HTTPException(status_code=500, detail=error_msg)

@app.post("/api/browser/new_chat")
async def start_new_chat():
    global browser_ctrl
    if not browser_ctrl or not browser_ctrl.is_connected():
        # If not connected, we don't have to raise an error, just return success
        return {"status": "success", "message": "Browser not connected, skipped tab reset."}
        
    urls = {
        "chatgpt": "https://chatgpt.com",
        "gemini": "https://gemini.google.com",
        "deepseek": "https://chat.deepseek.com",
        "claude": "https://claude.ai"
    }
    
    tasks = []
    for keyword, url in urls.items():
        try:
            tab = await browser_ctrl.find_tab(keyword)
            if tab:
                tasks.append(tab.goto(url, timeout=20000))
        except Exception as te:
            print(f"Error finding tab for {keyword}: {te}")
            
    if tasks:
        await asyncio.gather(*tasks, return_exceptions=True)
        
    return {"status": "success", "message": "New chat initialized in all tabs."}

@app.post("/api/query")
async def run_query(payload: QueryPayload):
    global browser_ctrl
    if not browser_ctrl:
        raise HTTPException(status_code=400, detail="Browser not launched or connected. Please launch first.")

    supported_agents = {"chatgpt", "gemini", "deepseek"}
    requested_agents = []
    for agent in payload.agents:
        normalized_agent = agent.lower().strip()
        if normalized_agent not in supported_agents:
            raise HTTPException(status_code=400, detail=f"Unsupported agent selected: {agent}")
        if normalized_agent not in requested_agents:
            requested_agents.append(normalized_agent)

    if not requested_agents:
        raise HTTPException(status_code=400, detail="Please select at least one AI agent.")
        
    # Verify we can read tabs
    try:
        browser_ctrl.get_pages()
    except Exception as e:
        browser_ctrl = None
        raise HTTPException(status_code=400, detail="Browser connection lost. Please relaunch.")

    # Check which selected agents are open
    missing_agents = []
    for agent in requested_agents:
        if not await browser_ctrl.find_tab(agent):
            missing_agents.append(agent)
            
    claude_page = await browser_ctrl.find_tab("claude") if payload.synthesize else None
    if payload.synthesize and not claude_page:
        missing_agents.append("claude")
        
    if missing_agents:
        raise HTTPException(
            status_code=400, 
            detail=f"Please open tabs for missing tools first: {', '.join(missing_agents)}"
        )

    saved_file_paths = []
    temp_dir = os.path.join(os.getcwd(), "temp_uploads")
    if payload.files:
        import base64
        import re
        import time
        os.makedirs(temp_dir, exist_ok=True)
        for f in payload.files:
            try:
                base64_data = f.data
                if "," in base64_data:
                    base64_data = base64_data.split(",", 1)[1]
                file_bytes = base64.b64decode(base64_data)
                safe_name = re.sub(r'[^a-zA-Z0-9._-]', '_', f.name)
                unique_name = f"{int(time.time() * 1000)}_{safe_name}"
                temp_path = os.path.abspath(os.path.join(temp_dir, unique_name))
                with open(temp_path, "wb") as fh:
                    fh.write(file_bytes)
                saved_file_paths.append(temp_path)
            except Exception as fe:
                print(f"Error saving temp file {f.name}: {fe}")

    try:
        question = payload.question
        agents = AIAgents(browser_ctrl)
        
        # Step 1: Broadcast prompt to all active agents concurrently
        print(f"Broadcasting question to: {requested_agents}")
        agent_pages = await agents.ask_all(question, active_agents=requested_agents, file_paths=saved_file_paths)
        if not agent_pages:
            raise HTTPException(status_code=500, detail="Could not send the question to any selected AI tab.")
        
        # Step 2: Concurrently wait for responses to finish and extract them
        print("Waiting for responses...")
        wait_tasks = []
        active_agent_names = list(agent_pages.keys())
        
        for agent_name, page in agent_pages.items():
            wait_tasks.append(wait_for_response_to_finish(page, agent_name))
            
        responses_list = await asyncio.gather(*wait_tasks)
        
        responses = {}
        for agent_name, response_text in zip(active_agent_names, responses_list):
            responses[agent_name] = response_text
            
        # Step 3: Synthesis via Claude tab (if enabled)
        synthesized_answer = None
        if payload.synthesize and claude_page:
            print("Sending responses to Claude for synthesis...")
            synthesizer = ClaudeSynthesizer(browser_ctrl)
            synthesized_answer = await synthesizer.synthesize(responses, question)
            
        return {
            "status": "completed",
            "responses": responses,
            "synthesized": synthesized_answer
        }
    finally:
        # Clean up temporary files
        if saved_file_paths:
            print("Cleaning up temporary uploaded files...")
            for temp_path in saved_file_paths:
                try:
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
                except Exception as clean_err:
                    print(f"Failed to remove temp file {temp_path}: {clean_err}")
            try:
                if os.path.exists(temp_dir) and not os.listdir(temp_dir):
                    os.rmdir(temp_dir)
            except:
                pass

@app.get("/api/history")
async def get_history():
    try:
        history = db.load_history()
        return {"status": "success", "history": history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/history")
async def save_history_turn(request: Request):
    try:
        turn_data = await request.json()
        db.save_turn(turn_data)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/history")
async def delete_history():
    try:
        db.clear_history()
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def select_browser_cli():
    print("\n==================================================================")
    print(" Please select the browser you want to use:")
    print(" 1. Chrome")
    print(" 2. Firefox")
    print(" 3. Brave")
    print(" 4. Edge")
    print(" 5. Opera")
    print(" 6. Other (Specify path)")
    print("==================================================================")
    try:
        choice = input("Enter choice (1-6): ").strip()
    except (KeyboardInterrupt, EOFError):
        print("\nUsing Brave as default.")
        return "brave"

    if choice == "1":
        return "chrome"
    elif choice == "2":
        return "firefox"
    elif choice == "3" or choice == "":
        return "brave"
    elif choice == "4":
        return "edge"
    elif choice == "5":
        return "opera"
    elif choice == "6":
        try:
            custom_path = input("Enter custom browser executable path: ").strip().strip('"').strip("'")
            if custom_path and os.path.exists(custom_path):
                return custom_path
            else:
                print("Path does not exist or invalid. Defaulting to Brave.")
                return "brave"
        except (KeyboardInterrupt, EOFError):
            return "brave"
    else:
        print("Invalid choice. Defaulting to Brave.")
        return "brave"


if __name__ == "__main__":
    import uvicorn
    import sys
    import asyncio
    import warnings
    
    # Prompt user for browser choice
    selected_browser = select_browser_cli()
    current_browser_name = selected_browser

    if sys.platform == 'win32':
        # Prevent uvicorn from forcing WindowsSelectorEventLoopPolicy which breaks subprocesses
        try:
            from uvicorn.loops import asyncio as uvicorn_asyncio
            uvicorn_asyncio.asyncio_setup = lambda *args, **kwargs: None
        except ImportError:
            pass
            
        warnings.filterwarnings("ignore", category=DeprecationWarning)
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        
    uvicorn.run(app, host="127.0.0.1", port=8000)
