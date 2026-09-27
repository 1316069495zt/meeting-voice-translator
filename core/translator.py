from openai import OpenAI

class Translator:
    """
    智能翻译引擎：
    针对远程外企技术面试与工作场景进行 Prompt 定制优化。
    """
    def __init__(self, api_key: str = "", base_url: str = "https://api.deepseek.com", model: str = "deepseek-chat"):
        self.api_key = api_key.strip()
        self.base_url = base_url.strip()
        self.model = model.strip()
        self._init_client()

    def _init_client(self):
        if self.api_key:
            self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        else:
            self.client = None

    def update_config(self, api_key: str, base_url: str, model: str):
        self.api_key = api_key.strip()
        self.base_url = base_url.strip()
        self.model = model.strip()
        self._init_client()

    def translate_to_english(self, chinese_text: str) -> str:
        """
        中文口语 -> 专业外企程序员英文口语
        """
        if not chinese_text.strip():
            return ""
        if not self.client:
            return chinese_text

        system_prompt = (
            "You are an expert real-time voice translator for a software engineer during an English technical interview or meeting.\n"
            "Translate the user's spoken Chinese into natural, concise, and professional spoken English.\n"
            "Rules:\n"
            "1. Output ONLY the translated English sentence.\n"
            "2. Do NOT add quotation marks, explanations, or introductory text.\n"
            "3. Use standard tech terminology (e.g., latency, cache, deadlock, microservices).\n"
            "4. Keep sentences punchy and conversational suitable for voice synthesis."
        )

        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": chinese_text}
                ],
                temperature=0.2,
                max_tokens=80
            )
            return resp.choices[0].message.content.strip()
        except Exception as e:
            print(f"[Translator] 翻译异常: {e}")
            return f"[翻译错误: {str(e)}]"

    def translate_to_chinese(self, english_text: str) -> str:
        """
        英文会议语音 -> 简洁易懂的中文字幕
        """
        if not english_text.strip():
            return ""
        if not self.client:
            return english_text

        system_prompt = (
            "You are a real-time subtitle translator.\n"
            "Translate the English speech into clear, concise, fluent Chinese subtitle for a Chinese developer.\n"
            "Output ONLY the translated Chinese text without explanations."
        )

        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": english_text}
                ],
                temperature=0.1,
                max_tokens=100
            )
            return resp.choices[0].message.content.strip()
        except Exception as e:
            print(f"[Translator] 字幕翻译异常: {e}")
            return f"[字幕翻译错误: {str(e)}]"
