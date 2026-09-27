import asyncio
import io
import edge_tts
from pydub import AudioSegment

class TTSEngine:
    """
    高保真低延迟语音合成引擎（基于 Microsoft Edge 神经网络语音，免费且极度逼真）
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

        mp3_data = mp3_buffer.getvalue()
        if not mp3_data:
            return b""

        # 将 MP3 转为标准 PCM WAV 格式供 sounddevice 顺畅播放
        audio = AudioSegment.from_file(io.BytesIO(mp3_data), format="mp3")
        wav_buffer = io.BytesIO()
        audio.export(wav_buffer, format="wav")
        return wav_buffer.getvalue()

    def synthesize(self, text: str) -> bytes:
        """同步调用接口返回 WAV 音频二进制"""
        if not text.strip():
            return b""
        try:
            return asyncio.run(self._synthesize_async(text))
        except Exception as e:
            print(f"[TTSEngine] 语音合成失败: {e}")
            return b""
