# -*- coding: utf-8 -*-
import json
import os
import sys

DEFAULT_CONFIG = {
    "provider": "Groq (免费极速·推荐)",
    "base_url": "https://api.groq.com/openai/v1",
    "model": "qwen/qwen3.8-27b",
    "api_key": "",
    "target_language": "🇺🇸 英语 (English)",
    "voice": "en-US-ChristopherNeural",
    "mic_name": "",
    "cable_name": "",
    "monitor_name": "",
    "custom_terms": "Kubernetes, CUDA, Raft, Microservices, PyTorch, Latency, Deadlock",
    "save_audio": True,
    "ptt_mode": "hold",        # "hold" (按住说话) 或 "toggle" (点击开关)
    "global_hotkey": "F8"      # 全局快捷键
}

class ConfigManager:
    """
    配置持久化管理器：
    在程序关闭或设置变更时自动存盘为 config.json，启动时无缝回显。
    """
    def __init__(self, filename="config.json"):
        # 兼容 PyInstaller 打包环境与源码运行环境
        if getattr(sys, 'frozen', False):
            base_dir = os.path.dirname(sys.executable)
        else:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            
        self.filepath = os.path.join(base_dir, filename)
        self.data = self.load()

    def load(self) -> dict:
        if not os.path.exists(self.filepath):
            return DEFAULT_CONFIG.copy()
        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                saved = json.load(f)
                config = DEFAULT_CONFIG.copy()
                config.update(saved)
                return config
        except Exception as e:
            print(f"[ConfigManager] 读取配置文件异常: {e}")
            return DEFAULT_CONFIG.copy()

    def save(self, **kwargs):
        self.data.update(kwargs)
        try:
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[ConfigManager] 保存配置失败: {e}")

    def get(self, key, default=None):
        return self.data.get(key, default)
