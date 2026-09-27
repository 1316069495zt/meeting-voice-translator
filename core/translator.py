# -*- coding: utf-8 -*-
from openai import OpenAI
from core.languages import LANGUAGE_CONFIGS

class Translator:
    """
    智能多语种翻译引擎：
    针对海外远程技术面试与外企研发场景进行深度 Prompt 调优，
    支持英、日、德、法、韩、西等全球主流研发语言的高保真专业口语互译。
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

    def translate_speech(self, chinese_text: str, target_lang_name: str = "🇺🇸 英语 (English)", custom_terms: str = "") -> str:
        """
        中文口语 -> 专业外语研发口语（带简历技术术语库偏置）
        """
        if not chinese_text.strip():
            return ""
        if not self.client:
            return chinese_text

        lang_cfg = LANGUAGE_CONFIGS.get(target_lang_name, LANGUAGE_CONFIGS["🇺🇸 英语 (English)"])
        system_prompt = lang_cfg["prompt_template"]

        if custom_terms and custom_terms.strip():
            system_prompt += (
                f"\n\n[Important Technical Terms & Context to match accurately]:\n"
                f"{custom_terms.strip()}\n"
                "Ensure these technical acronyms/frameworks are preserved accurately in standard capitalization."
            )

        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": chinese_text}
                ],
                temperature=0.15,
                max_tokens=150
            )
            return resp.choices[0].message.content.strip()
        except Exception as e:
            print(f"[Translator] 翻译异常: {e}")
            return f"[翻译错误: {str(e)}]"

    def translate_to_english(self, chinese_text: str, custom_terms: str = "") -> str:
        return self.translate_speech(chinese_text, "🇺🇸 英语 (English)", custom_terms)

    def translate_to_chinese(self, foreign_text: str) -> str:
        """外语原声 -> 简明易懂的中文实时字幕"""
        if not foreign_text.strip():
            return ""
        if not self.client:
            return foreign_text

        system_prompt = (
            "You are a real-time subtitle translator.\n"
            "Translate the foreign speech into clear, concise, fluent Chinese subtitle for a Chinese software engineer.\n"
            "Output ONLY the translated Chinese text without explanations."
        )

        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": foreign_text}
                ],
                temperature=0.1,
                max_tokens=120
            )
            return resp.choices[0].message.content.strip()
        except Exception as e:
            print(f"[Translator] 字幕翻译异常: {e}")
            return f"[字幕翻译错误: {str(e)}]"
