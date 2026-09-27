import asyncio
import io
import edge_tts

class TTSEngine:
    """
    高保真超低延迟语音合成引擎（基于 Microsoft Edge 神经网络语音，免 API Key、零成本、毫秒级首包）
    """
    def __init__(self, voice: str = "en-US-ChristopherNeural", rate: str = "+5%"):
        self.voice = voice
        self.rate = rate

    def update_voice(self, voice: str, rate: str = "+5%"):
        self.voice = voice
        self.rate = rate

    async def _synthesize_async(self, text: str) -> bytes:
        communicate = edge_tts.Communicate(text, voice=self.voice, rate=self.rate)
        mp3_buffer = io.BytesIO()
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                mp3_buffer.write(chunk["data"])

        return mp3_buffer.getvalue()

    def synthesize(self, text: str) -> bytes:
        """返回音频二进制数据"""
        if not text.strip():
            return b""
        try:
            return asyncio.run(self._synthesize_async(text))
        except Exception as e:
            print(f"[TTSEngine] 语音合成失败: {e}")
            return b""
