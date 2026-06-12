import asyncio

class AIAgents:
    def __init__(self, browser_controller):
        self.browser = browser_controller

    async def upload_files(self, page, file_paths):
        if not file_paths:
            return
        try:
            print(f"Uploading {len(file_paths)} files to {page.url}...")
            # Target the first file input
            file_input = page.locator('input[type="file"]').first
            await file_input.wait_for(state="attached", timeout=5000)
            await file_input.set_input_files(file_paths)
            # Wait for upload to initiate/render
            await asyncio.sleep(2.0)
        except Exception as e:
            print(f"Error uploading files to page {page.url}: {e}")

    async def send_message_chatgpt(self, page, message, file_paths=None):
        if file_paths:
            await self.upload_files(page, file_paths)
            
        # Find ChatGPT textarea
        textarea = page.locator('textarea#prompt-textarea, textarea[placeholder*="ChatGPT"], textarea, div[contenteditable="true"]').first
        await textarea.wait_for(state="visible", timeout=10000)
        await textarea.focus()
        await textarea.fill(message)
        
        # Trigger input events in case the framework missed it
        await textarea.press("Space")
        await textarea.press("Backspace")
        await asyncio.sleep(0.5)
        
        # Send
        await page.keyboard.press("Enter")

    async def send_message_gemini(self, page, message, file_paths=None):
        if file_paths:
            await self.upload_files(page, file_paths)
            
        # Find Gemini text box (usually contenteditable div with role="textbox")
        textbox = page.locator('div[role="textbox"], textarea, div[contenteditable="true"]').first
        await textbox.wait_for(state="visible", timeout=10000)
        await textbox.focus()
        await textbox.fill(message)
        
        await textbox.press("Space")
        await textbox.press("Backspace")
        await asyncio.sleep(0.5)
        
        await page.keyboard.press("Enter")

    async def send_message_deepseek(self, page, message, file_paths=None):
        if file_paths:
            await self.upload_files(page, file_paths)
            
        # Find DeepSeek textarea
        textarea = page.locator('textarea[placeholder*="DeepSeek"], textarea[placeholder*="message"], textarea, div[contenteditable="true"]').first
        await textarea.wait_for(state="visible", timeout=10000)
        await textarea.focus()
        await textarea.fill(message)
        
        await textarea.press("Space")
        await textarea.press("Backspace")
        await asyncio.sleep(0.5)
        
        await page.keyboard.press("Enter")

    async def ask_agent(self, agent_name, question, file_paths=None):
        """
        Finds the tab for the specified agent and sends the question.
        Returns the page if successful, else None.
        """
        page = await self.browser.find_tab(agent_name)
        if not page:
            print(f"Tab for {agent_name} not found. Cannot ask question.")
            return None
            
        try:
            if agent_name == "chatgpt":
                await self.send_message_chatgpt(page, question, file_paths)
            elif agent_name == "gemini":
                await self.send_message_gemini(page, question, file_paths)
            elif agent_name == "deepseek":
                await self.send_message_deepseek(page, question, file_paths)
            else:
                print(f"Unknown agent: {agent_name}")
                return None
            return page
        except Exception as e:
            print(f"Error sending message to {agent_name}: {e}")
            return None

    async def ask_all(self, question, active_agents=None, file_paths=None):
        """
        Sends the question to all active agents concurrently.
        """
        if active_agents is None:
            active_agents = ["chatgpt", "gemini", "deepseek"]
        tasks = []
        for agent in active_agents:
            tasks.append(self.ask_agent(agent, question, file_paths))
            
        results = await asyncio.gather(*tasks)
        
        # Map agent name to page
        agent_pages = {}
        for agent, page in zip(active_agents, results):
            if page:
                agent_pages[agent] = page
                
        return agent_pages
