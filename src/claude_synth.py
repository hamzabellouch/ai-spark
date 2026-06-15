import asyncio
from utils import wait_for_response_to_finish

class ClaudeSynthesizer:
    def __init__(self, browser_controller):
        self.browser = browser_controller

    async def synthesize(self, responses, original_question):
        """
        Sends the collected AI responses to the open Claude tab to generate
        a unified and enhanced response.
        """
        claude_page = await self.browser.find_tab("claude")
        if not claude_page:
            print("Claude tab not found. Skipping synthesis.")
            return "Claude tab not found. Showing individual responses."
            
        # Format the synthesis prompt in Arabic since the user's focus is Arabic
        prompt = f"""
أنت خبير استراتيجي في دمج وتحليل إجابات الذكاء الاصطناعي المتعددة.
لقد طرح المستخدم السؤال التالي:
"{original_question}"

لقد جمعنا إجابات من (ChatGPT و Gemini و DeepSeek) على هذا السؤال.
مهمتك ليست مجرد التلخيص السطحي، بل "استخلاص أقصى قدر من التفاصيل الدقيقة والعميقة" من هذه الإجابات، لإنتاج إجابة "شاملة، مفصلة جداً، وموسعة" باللغة العربية.
1. اذكر كافة التفاصيل، الحلول، والشروحات المعطاة ولا تحذف أي نقطة مهمة.
2. إذا كان هناك أكواد برمجية أو خطوات عملية، ادمجها بشكل احترافي ومفصل دون اختصار.
3. تجنب التكرار، وصحح أي تعارضات بذكاء، مع الحفاظ على كل المعلومات الثمينة التي قدمها كل نموذج.
4. اكتب الرد النهائي بتنسيق Markdown جميل، دقيق، ومنظم باحترافية لتجربة قراءة ممتازة.

إليك الإجابات المستخرجة:

---
[إجابة ChatGPT]:
{responses.get('chatgpt', 'لم يتم استخراج إجابة.')}

---
[إجابة Gemini]:
{responses.get('gemini', 'لم يتم استخراج إجابة.')}

---
[إجابة DeepSeek]:
{responses.get('deepseek', 'لم يتم استخراج إجابة.')}
---
"""

        try:
            # Find Claude text area - .last is safer to get the main input at the bottom
            textbox = claude_page.locator('.ProseMirror, div[contenteditable="true"], div[role="textbox"], textarea').last
            await textbox.wait_for(state="visible", timeout=10000)
            await textbox.focus()
            
            # Select all and delete to clear without breaking ProseMirror's internal state
            await claude_page.keyboard.press("Control+A")
            await claude_page.keyboard.press("Backspace")
            await asyncio.sleep(0.5)
            
            # Insert the new prompt
            await claude_page.keyboard.insert_text(prompt)
            await asyncio.sleep(0.5)
            
            # Ensure we trigger input events
            await claude_page.keyboard.press("Space")
            await claude_page.keyboard.press("Backspace")
            await asyncio.sleep(0.5)
            
            # Send using keyboard Enter (with Control for multi-line)
            await claude_page.keyboard.press("Control+Enter")
            await claude_page.keyboard.press("Enter")
            await asyncio.sleep(0.5)
            
            # Robust fallback: click the send button via JS
            try:
                await claude_page.evaluate('''() => {
                    const btns = Array.from(document.querySelectorAll('button'));
                    const sendBtn = btns.find(b => {
                        const aria = (b.getAttribute('aria-label') || '').toLowerCase();
                        return aria.includes('send') || aria.includes('إرسال') || b.innerHTML.includes('send');
                    });
                    if(sendBtn && !sendBtn.disabled) {
                        sendBtn.click();
                    }
                }''')
            except Exception as js_e:
                print(f"JS send button click failed: {js_e}")
                
            # Wait for Claude to finish generating
            final_answer = await wait_for_response_to_finish(claude_page, "claude")
            return final_answer
            
        except Exception as e:
            print(f"Error communicating with Claude tab: {e}")
            return f"Error communicating with Claude: {e}"
