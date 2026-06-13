import asyncio
from browser import BrowserController

async def main():
    b = BrowserController('chrome')
    print("Launching...")
    try:
        await b.launch_browser(force_kill=True)
        print("Launched successfully")
        await b.connect()
        print("Connected successfully")
        await b.close()
    except Exception as e:
        print(f"Error: {e}")

asyncio.run(main())
