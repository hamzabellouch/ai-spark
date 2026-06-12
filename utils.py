import asyncio

async def get_last_element_text(page, selector):
    """
    Finds all elements matching selector and returns the inner text of the last one.
    """
    try:
        js_code = '''(sel) => {
            const extractMd = (el) => {
                if (!el) return "";
                const clone = el.cloneNode(true);
                const pres = clone.querySelectorAll('pre');
                pres.forEach(pre => {
                    let lang = '';
                    const codeEl = pre.querySelector('code');
                    if (codeEl && codeEl.className) {
                        const match = codeEl.className.match(/language-(\\w+)/);
                        if (match) lang = match[1];
                    }
                    if (!lang) {
                        const langDiv = pre.querySelector('.language-id, [class*="language"], .text-xs');
                        if (langDiv) lang = langDiv.innerText.trim();
                    }
                    const copyBtns = pre.querySelectorAll('button, svg, .copy-button');
                    copyBtns.forEach(b => b.remove());
                    
                    let codeText = codeEl ? (codeEl.innerText || codeEl.textContent) : (pre.innerText || pre.textContent);
                    const textNode = document.createTextNode(`\\n\\n\`\`\`${lang}\\n${codeText.trim()}\\n\`\`\`\\n\\n`);
                    pre.parentNode.replaceChild(textNode, pre);
                });
                const tables = clone.querySelectorAll('table');
                tables.forEach(table => {
                    let mdTable = '\\n\\n';
                    const rows = table.querySelectorAll('tr');
                    rows.forEach((row, rowIndex) => {
                        let mdRow = '|';
                        const cells = row.querySelectorAll('th, td');
                        cells.forEach(cell => {
                            mdRow += ' ' + (cell.innerText || cell.textContent).trim().replace(/\\n/g, ' ') + ' |';
                        });
                        mdTable += mdRow + '\\n';
                        if (rowIndex === 0) {
                            let sepRow = '|';
                            cells.forEach(() => { sepRow += '---|'; });
                            mdTable += sepRow + '\\n';
                        }
                    });
                    mdTable += '\\n';
                    const textNode = document.createTextNode(mdTable);
                    table.parentNode.replaceChild(textNode, table);
                });
                
                const codes = clone.querySelectorAll('code');
                codes.forEach(code => {
                    if (code.closest('pre')) return;
                    const textNode = document.createTextNode(` \`${code.innerText || code.textContent}\` `);
                    code.parentNode.replaceChild(textNode, code);
                });
                
                const strongs = clone.querySelectorAll('strong, b');
                strongs.forEach(strong => {
                    const textNode = document.createTextNode(`**${strong.innerText || strong.textContent}**`);
                    strong.parentNode.replaceChild(textNode, strong);
                });
                
                return clone.innerText || clone.textContent || "";
            };
            
            const els = document.querySelectorAll(sel);
            if (els.length > 0) {
                return extractMd(els[els.length - 1]);
            }
            return "";
        }'''
        
        text = await page.evaluate(js_code, selector)
        if text and text.strip():
            return text
                
        # Fallback: broad search for common AI message containers
        fallback_js = '''() => {
            const extractMd = (el) => {
                if (!el) return "";
                const clone = el.cloneNode(true);
                const pres = clone.querySelectorAll('pre');
                pres.forEach(pre => {
                    let lang = '';
                    const codeEl = pre.querySelector('code');
                    if (codeEl && codeEl.className) {
                        const match = codeEl.className.match(/language-(\\w+)/);
                        if (match) lang = match[1];
                    }
                    if (!lang) {
                        const langDiv = pre.querySelector('.language-id, [class*="language"], .text-xs');
                        if (langDiv) lang = langDiv.innerText.trim();
                    }
                    const copyBtns = pre.querySelectorAll('button, svg, .copy-button');
                    copyBtns.forEach(b => b.remove());
                    
                    let codeText = codeEl ? (codeEl.innerText || codeEl.textContent) : (pre.innerText || pre.textContent);
                    const textNode = document.createTextNode(`\\n\\n\`\`\`${lang}\\n${codeText.trim()}\\n\`\`\`\\n\\n`);
                    pre.parentNode.replaceChild(textNode, pre);
                });
                const tables = clone.querySelectorAll('table');
                tables.forEach(table => {
                    let mdTable = '\\n\\n';
                    const rows = table.querySelectorAll('tr');
                    rows.forEach((row, rowIndex) => {
                        let mdRow = '|';
                        const cells = row.querySelectorAll('th, td');
                        cells.forEach(cell => {
                            mdRow += ' ' + (cell.innerText || cell.textContent).trim().replace(/\\n/g, ' ') + ' |';
                        });
                        mdTable += mdRow + '\\n';
                        if (rowIndex === 0) {
                            let sepRow = '|';
                            cells.forEach(() => { sepRow += '---|'; });
                            mdTable += sepRow + '\\n';
                        }
                    });
                    mdTable += '\\n';
                    const textNode = document.createTextNode(mdTable);
                    table.parentNode.replaceChild(textNode, table);
                });
                
                const codes = clone.querySelectorAll('code');
                codes.forEach(code => {
                    if (code.closest('pre')) return;
                    const textNode = document.createTextNode(` \`${code.innerText || code.textContent}\` `);
                    code.parentNode.replaceChild(textNode, code);
                });
                
                const strongs = clone.querySelectorAll('strong, b');
                strongs.forEach(strong => {
                    const textNode = document.createTextNode(`**${strong.innerText || strong.textContent}**`);
                    strong.parentNode.replaceChild(textNode, strong);
                });
                
                return clone.innerText || clone.textContent || "";
            };

            const els = document.querySelectorAll('.font-claude-response, .standard-markdown, .prose, .font-claude-message, [data-testid="message-content"], .markdown, .ds-markdown, div[data-message-author-role="assistant"]');
            if (els.length > 0) {
                return extractMd(els[els.length - 1]);
            }
            // Super fallback: find the last large text block
            const divs = document.querySelectorAll('div');
            for (let i = divs.length - 1; i >= 0; i--) {
                const t = divs[i].innerText || divs[i].textContent || "";
                if (t.length > 30) return extractMd(divs[i]);
            }
            return "";
        }'''
        fallback_text = await page.evaluate(fallback_js)
        if fallback_text and fallback_text.strip():
            return fallback_text
            
    except Exception as e:
        print(f"Error getting text for selector {selector}: {e}")
    return ""

async def wait_for_response_to_finish(page, agent_name, timeout=90):
    """
    Waits for the AI response to stop generating.
    Uses a fast-polling state machine checking for Stop buttons and monitoring text stability.
    """
    print(f"Waiting for {agent_name} to finish generating...")
    
    # Platform-specific selectors for the assistant messages
    selectors = {
        "chatgpt": 'div[data-message-author-role="assistant"] .markdown, div[data-message-author-role="assistant"]',
        "gemini": 'message-content div.markdown, .message-content, div.markdown',
        "deepseek": '.ds-markdown, div.markdown',
        "claude": '.font-claude-response, .standard-markdown, [data-testid="message-content"], .font-claude-message, .prose, div.markdown, div[role="article"]'
    }
    
    selector = selectors.get(agent_name, 'div.markdown')
    
    # Capture initial state to detect when generation starts
    initial_count = 0
    initial_text = ""
    try:
        initial_text = await get_last_element_text(page, selector)
        initial_count = await page.evaluate(f'''(sel) => document.querySelectorAll(sel).length''', selector)
    except Exception as e:
        print(f"Error capturing initial state for {agent_name}: {e}")

    loop = asyncio.get_running_loop()
    start_time = loop.time()
    
    stop_buttons = {
        "chatgpt": 'button[data-testid="stop-button"]',
        "gemini": 'button[aria-label*="Stop"], button[aria-label*="stop"]',
        "deepseek": 'button:has(svg):has-text("Stop"), button[aria-label*="Stop"], button[class*="stop"]',
        "claude": 'button[aria-label*="Stop"], button[aria-label*="stop"]'
    }
    stop_selector = stop_buttons.get(agent_name)
    
    # Phase 1: Wait for generation to start (Max 8.0 seconds for large prompts)
    started = False
    print(f"[{agent_name}] Phase 1: Waiting for generation to start...")
    while loop.time() - start_time < 8.0:
        if stop_selector:
            try:
                if await page.locator(stop_selector).first.is_visible():
                    started = True
            except:
                pass
        
        try:
            current_count = await page.evaluate(f'''(sel) => document.querySelectorAll(sel).length''', selector)
            if current_count > initial_count:
                started = True
            elif current_count > 0:
                current_text = await get_last_element_text(page, selector)
                if current_text != initial_text and len(current_text.strip()) > 0:
                    started = True
        except:
            pass
            
        if started:
            print(f"[{agent_name}] Generation started detected.")
            break
            
        await asyncio.sleep(0.1)
        
    # Phase 2: Monitor generation
    print(f"[{agent_name}] Phase 2: Monitoring generation...")
    last_text = ""
    stable_ticks = 0
    stop_button_seen = False
    
    if stop_selector:
        try:
            if await page.locator(stop_selector).first.is_visible():
                stop_button_seen = True
        except:
            pass

    poll_interval = 0.2
    
    while loop.time() - start_time < timeout:
        is_stop_visible = False
        # 1. Stop button check
        if stop_selector:
            try:
                is_stop_visible = await page.locator(stop_selector).first.is_visible()
                if is_stop_visible:
                    stop_button_seen = True
                elif stop_button_seen:
                    await asyncio.sleep(0.1)
                    if not await page.locator(stop_selector).first.is_visible():
                        final_text = await get_last_element_text(page, selector)
                        print(f"[{agent_name}] Stop button disappeared. Finished generating.")
                        return final_text
            except Exception as e:
                pass # ignore if not found
                
        # 2. Text stability check (only if stop button is NOT visible)
        if not is_stop_visible:
            current_text = await get_last_element_text(page, selector)
            if current_text:
                current_text_stripped = current_text.strip()
                if current_text_stripped == last_text and len(current_text_stripped) > 0:
                    stable_ticks += 1
                    if stable_ticks >= 5:  # 5 ticks * 0.2s = 1.0s
                        print(f"[{agent_name}] Text stabilized for 1.0s without stop button. Finished generating.")
                        return current_text
                else:
                    stable_ticks = 0
                    last_text = current_text_stripped
            else:
                stable_ticks = 0
        else:
            # If stop button is visible, reset stable ticks because it's still actively generating/thinking
            stable_ticks = 0
            
        await asyncio.sleep(poll_interval)
        
    print(f"[{agent_name}] Timeout reached. Returning last text.")
    return await get_last_element_text(page, selector)

async def extract_response(page, agent_name):
    """
    Extracts the final response text from the agent tab.
    """
    selectors = {
        "chatgpt": 'div[data-message-author-role="assistant"] .markdown, div[data-message-author-role="assistant"]',
        "gemini": 'message-content div.markdown, .message-content, div.markdown',
        "deepseek": '.ds-markdown, div.markdown',
        "claude": '.font-claude-response, .standard-markdown, [data-testid="message-content"], .font-claude-message, .prose, div.markdown, div[role="article"]'
    }
    selector = selectors.get(agent_name, 'div.markdown')
    text = await get_last_element_text(page, selector)
    if not text:
        # Fallback to general markdown or last paragraphs
        text = await get_last_element_text(page, 'div.markdown')
    return text
