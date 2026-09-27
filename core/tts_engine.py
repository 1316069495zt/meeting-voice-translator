# -*- coding: utf-8 -*-
import asyncio
import io
import edge_tts

class TTSEngine:
    """
    超低延迟高保真多语种语音合成引擎（基于 Microsoft Edge 神经网络官方音色，免 API Key、零成本、毫秒级响应）
    """
    def __init__(self, voice: str = "en-US-ChristopherNeural", rate: str = "+5%"):
        self.voice = voice
        self.rate = rate

    def update_voice(self, voice: str, rate: str = "+5%"):
        self.voice = voice.strip()
        self.rate = rate.strip()

    async def _synthesize_async(self, text: str) -> bytes:
        communicate = edge_tts.Communicate(text, voice=self.voice, rate=self.rate)
        mp3_buffer = io.BytesIO()
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                mp3_buffer.write(chunk["data"])

        return mp3_buffer.getvalue()

    def synthesize(self, text: str) -> bytes:
        """返回音频二进制数据 (MP3 格式)"""
        if not text or not text.strip():
            return b""
        try:
            return asyncio.run(self._synthesize_async(text))
        except Exception as e:
            print(f"[TTSEngine] 语音合成失败 (voice: {self.voice}): {e}")
            # 优雅降级：如果某些特定音色受限，自动尝试英文默认音色
            try:
                communicate = edge_tts.Communicate(text, voice="en-US-ChristopherNeural", rate="+5%")
                mp3_buffer = io.BytesIO()
                async def _fallback():
                    async for chunk in communicate.stream():
                        if chunk["type"] == "audio":
                            mp3_buffer.write(chunk["data"])
                    return mp3_buffer.getvalue()
                return asyncio.run(_fallback())
            except Exception as e2:
                print(f"[TTSEngine] 降级合成亦失败: {e2}")
                return b""
