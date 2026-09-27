import io
import requests

class STTEngine:
    """
    语音转文字引擎（支持 OpenAI、Groq、SiliconFlow 等兼容接口的 Whisper 模型）
    """
    def __init__(self, api_key: str = "", base_url: str = "https://api.openai.com/v1"):
        self.api_key = api_key.strip()
        self.base_url = base_url.rstrip("/")
        if not self.base_url.endswith("/v1"):
            # 常见服务商自动兼容
            if "deepseek" in self.base_url:
                pass
            elif not self.base_url.endswith("/v1"):
                self.base_url += "/v1"

    def update_config(self, api_key: str, base_url: str):
        self.api_key = api_key.strip()
        self.base_url = base_url.rstrip("/")

    def transcribe(self, audio_wav_bytes: bytes, language: str = "zh") -> str:
        """
        上传音频二进制数据，返回识别后的文本
        """
        if not audio_wav_bytes or len(audio_wav_bytes) < 1000:
            return ""

        if not self.api_key:
            return "【错误：未配置 API Key】"

        url = f"{self.base_url}/audio/transcriptions"
        headers = {
            "Authorization": f"Bearer {self.api_key}"
        }

        # 默认使用 whisper-1，Groq 使用 whisper-large-v3
        model = "whisper-1"
        if "groq" in self.base_url:
            model = "whisper-large-v3"

        files = {
            "file": ("speech.wav", io.BytesIO(audio_wav_bytes), "audio/wav")
        }
        data = {
            "model": model,
            "language": language,
            "temperature": "0.0"
        }

        try:
            resp = requests.post(url, headers=headers, files=files, data=data, timeout=12)
            if resp.status_code == 200:
                result = resp.json()
                return result.get("text", "").strip()
            else:
                return f"[识别失败: HTTP {resp.status_code}]"
        except Exception as e:
            return f"[识别异常: {str(e)}]"
