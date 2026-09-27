import sounddevice as sd
import numpy as np
import soundfile as sf
import io
import threading
import queue

class AudioRouter:
    """
    音频路由管理器：
    负责检测系统声卡、识别 VB-CABLE 虚拟麦克风通道、录音与推流。
    """
    def __init__(self):
        self.sample_rate = 16000
        self.channels = 1
        self.recording_queue = queue.Queue()
        self.is_recording = False
        self.stream = None

    @staticmethod
    def get_devices():
        """获取系统所有输入与输出设备"""
        devices = sd.query_devices()
        inputs = []
        outputs = []
        vb_cable_input_id = None
        vb_cable_output_id = None

        for idx, dev in enumerate(devices):
            name = dev['name']
            if dev['max_input_channels'] > 0:
                inputs.append({"id": idx, "name": name})
                if "CABLE Output" in name:
                    vb_cable_output_id = idx

            if dev['max_output_channels'] > 0:
                outputs.append({"id": idx, "name": name})
                if "CABLE Input" in name:
                    vb_cable_input_id = idx

        return {
            "inputs": inputs,
            "outputs": outputs,
            "vb_cable_input_id": vb_cable_input_id,     # Python 推送英文音频写入此设备
            "vb_cable_output_id": vb_cable_output_id    # 会议软件（浏览器）麦克风应选此设备
        }

    def start_recording(self, input_device_id=None):
        """开始录制麦克风音频"""
        self.is_recording = True
        self.recording_queue = queue.Queue()

        def callback(indata, frames, time, status):
            if self.is_recording:
                self.recording_queue.put(indata.copy())

        self.stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=self.channels,
            dtype='int16',
            device=input_device_id,
            callback=callback
        )
        self.stream.start()

    def stop_recording(self) -> bytes:
        """停止录音并返回 WAV 格式二进制音频"""
        self.is_recording = False
        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None

        audio_frames = []
        while not self.recording_queue.empty():
            audio_frames.append(self.recording_queue.get())

        if not audio_frames:
            return b""

        audio_data = np.concatenate(audio_frames, axis=0)
        wav_io = io.BytesIO()
        sf.write(wav_io, audio_data, self.sample_rate, format='WAV', subtype='PCM_16')
        return wav_io.getvalue()

    @staticmethod
    def play_audio(audio_bytes: bytes, target_device_id: int = None, local_monitor_id: int = None):
        """
        将音频数据推流到指定设备（如 VB-CABLE Input），同时可选择在耳机进行本地监听
        """
        try:
            data, fs = sf.read(io.BytesIO(audio_bytes))

            # 1. 播放到虚拟声卡（传给远程会议面试官）
            if target_device_id is not None:
                sd.play(data, samplerate=fs, device=target_device_id)

            # 2. 本地耳机同步监听
            if local_monitor_id is not None and local_monitor_id != target_device_id:
                # 另起线程同步监听
                threading.Thread(
                    target=lambda: sd.play(data, samplerate=fs, device=local_monitor_id),
                    daemon=True
                ).start()

            if target_device_id is not None:
                sd.wait()
        except Exception as e:
            print(f"[AudioRouter] 播放推流失败: {e}")
