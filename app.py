import sys
import threading
import time
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QComboBox, QLineEdit, QTextEdit,
    QGroupBox, QCheckBox, QMessageBox, QTabWidget
)
from PySide6.QtCore import Qt, Signal, QObject
from PySide6.QtGui import QFont, QIcon

from core.audio_router import AudioRouter
from core.stt_engine import STTEngine
from core.translator import Translator
from core.tts_engine import TTSEngine
from ui.subtitle_window import SubtitleWindow

# 常见服务商预设映射表，彻底避免模型与 Base URL 不匹配报 404
PROVIDER_PRESETS = {
    "Groq (免费极速·推荐)": {
        "base_url": "https://api.groq.com/openai/v1",
        "models": ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"],
        "hint": "填入 Groq 的 gsk_... 免费密钥"
    },
    "OpenAI (官方)": {
        "base_url": "https://api.openai.com/v1",
        "models": ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"],
        "hint": "填入 OpenAI 的 sk-... 密钥"
    },
    "DeepSeek 官方": {
        "base_url": "https://api.deepseek.com",
        "models": ["deepseek-chat"],
        "hint": "填入 DeepSeek 的 sk-... 密钥 (注: 仅支持翻译，STT需配合Groq)"
    },
    "SiliconFlow (硅基流动)": {
        "base_url": "https://api.siliconflow.cn/v1",
        "models": ["Qwen/Qwen2.5-7B-Instruct", "deepseek-ai/DeepSeek-V3"],
        "hint": "填入硅基流动的 sk-... 密钥"
    },
    "自定义 (Custom)": {
        "base_url": "https://api.openai.com/v1",
        "models": ["gpt-4o-mini"],
        "hint": "手动输入 Base URL 与模型名称"
    }
}

class WorkerSignals(QObject):
    log = Signal(str)
    status = Signal(str)
    subtitle_update = Signal(str, str)
    finished = Signal()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Meeting Voice Copilot (外企双向实时音译电台)")
        self.resize(880, 700)

        # 核心模块初始化
        self.router = AudioRouter()
        self.stt = STTEngine()
        self.translator = Translator()
        self.tts = TTSEngine()

        self.subtitle_win = SubtitleWindow()
        self.signals = WorkerSignals()
        self.signals.log.connect(self.append_log)
        self.signals.status.connect(self.update_status)
        self.signals.subtitle_update.connect(self.subtitle_win.update_subtitles)

        self.is_recording = False
        self.init_ui()
        self.load_devices()

    def init_ui(self):
        self.setStyleSheet("""
            QMainWindow { background-color: #0f172a; color: #f8fafc; }
            QLabel { color: #cbd5e1; font-size: 13px; }
            QGroupBox {
                border: 1px solid #334155;
                border-radius: 8px;
                margin-top: 10px;
                font-weight: bold;
                color: #38bdf8;
                padding: 12px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QComboBox, QLineEdit {
                background-color: #1e293b;
                border: 1px solid #475569;
                border-radius: 6px;
                padding: 6px 10px;
                color: #f8fafc;
                font-size: 13px;
            }
            QComboBox:focus, QLineEdit:focus {
                border-color: #38bdf8;
            }
            QPushButton {
                background-color: #2563eb;
                color: white;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 13px;
                font-weight: 500;
            }
            QPushButton:hover { background-color: #1d4ed8; }
            QPushButton:pressed { background-color: #1e40af; }
            QTextEdit {
                background-color: #0b132b;
                border: 1px solid #334155;
                border-radius: 6px;
                color: #94a3b8;
                font-family: Consolas, monospace;
                font-size: 12px;
            }
        """)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(18, 14, 18, 14)

        # 顶部标题栏与状态指示
        header_layout = QHBoxLayout()
        title_label = QLabel("🎙️ Meeting Voice Copilot (外企全双工音译电台)")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #38bdf8;")
        self.status_label = QLabel("● 就绪")
        self.status_label.setStyleSheet("color: #10b981; font-size: 13px; font-weight: bold;")
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.status_label)
        main_layout.addLayout(header_layout)

        # 1. 声卡设备路由设置 (已消除重复物理麦克风)
        device_box = QGroupBox("🔊 1. 音频设备路由 (VB-CABLE 虚拟麦克风通道)")
        dev_layout = QVBoxLayout(device_box)

        # 物理麦克风
        mic_layout = QHBoxLayout()
        mic_layout.addWidget(QLabel("物理麦克风 (你的输入):"))
        self.combo_mic = QComboBox()
        mic_layout.addWidget(self.combo_mic, 1)
        dev_layout.addLayout(mic_layout)

        # 虚拟输出声卡 (CABLE Input)
        cable_layout = QHBoxLayout()
        cable_lbl = QLabel("会议输出声卡 (传给会议):")
        self.combo_cable = QComboBox()
        cable_layout.addWidget(cable_lbl)
        cable_layout.addWidget(self.combo_cable, 1)
        dev_layout.addLayout(cable_layout)

        # 本地耳机监听
        monitor_layout = QHBoxLayout()
        monitor_layout.addWidget(QLabel("耳机同步监听 (听到自己发声):"))
        self.combo_monitor = QComboBox()
        monitor_layout.addWidget(self.combo_monitor, 1)
        dev_layout.addLayout(monitor_layout)

        main_layout.addWidget(device_box)

        # 2. AI 翻译与语音配置 (带服务商一键联动预设)
        ai_box = QGroupBox("⚙️ 2. 大模型与服务商配置 (自动匹配模型防404)")
        ai_layout = QVBoxLayout(ai_box)

        row0 = QHBoxLayout()
        row0.addWidget(QLabel("AI 服务商预设:"))
        self.combo_provider = QComboBox()
        for p in PROVIDER_PRESETS.keys():
            self.combo_provider.addItem(p)
        self.combo_provider.currentIndexChanged.connect(self.on_provider_changed)
        row0.addWidget(self.combo_provider, 1)

        row0.addWidget(QLabel("翻译模型:"))
        self.combo_model = QComboBox()
        self.combo_model.setEditable(True)
        row0.addWidget(self.combo_model, 1)
        ai_layout.addLayout(row0)

        row1 = QHBoxLayout()
        row1.addWidget(QLabel("API Key:"))
        self.txt_api_key = QLineEdit()
        self.txt_api_key.setEchoMode(QLineEdit.Password)
        self.txt_api_key.setPlaceholderText("填入 Groq 的 gsk_... 免费密钥")
        row1.addWidget(self.txt_api_key, 1)

        row1.addWidget(QLabel("Base URL:"))
        self.txt_base_url = QLineEdit("https://api.groq.com/openai/v1")
        row1.addWidget(self.txt_base_url, 1)
        ai_layout.addLayout(row1)

        row2 = QHBoxLayout()
        row2.addWidget(QLabel("英文口语音色:"))
        self.combo_voice = QComboBox()
        self.combo_voice.addItems([
            "en-US-ChristopherNeural (沉稳商务男声)",
            "en-US-JennyNeural (自然亲切女声)",
            "en-US-GuyNeural (经典美式男声)",
            "en-GB-RyanNeural (英伦绅士男声)"
        ])
        row2.addWidget(self.combo_voice, 1)
        ai_layout.addLayout(row2)

        main_layout.addWidget(ai_box)

        # 3. 核心对讲控制台
        ctrl_box = QGroupBox("🚀 3. 会议对讲与字幕控制台")
        ctrl_layout = QVBoxLayout(ctrl_box)

        btn_row = QHBoxLayout()
        self.btn_ptt = QPushButton("🎙️ 按住说话 (说中文 -> 自动转英文发声)")
        self.btn_ptt.setStyleSheet("""
            QPushButton {
                background-color: #10b981;
                font-size: 15px;
                font-weight: bold;
                padding: 13px;
            }
            QPushButton:hover { background-color: #059669; }
            QPushButton:pressed { background-color: #ef4444; }
        """)
        self.btn_ptt.pressed.connect(self.start_ptt)
        self.btn_ptt.released.connect(self.stop_ptt)
        btn_row.addWidget(self.btn_ptt, 2)

        self.btn_toggle_subtitle = QPushButton("📺 切换双语字幕悬浮窗")
        self.btn_toggle_subtitle.setStyleSheet("background-color: #6366f1; padding: 13px; font-weight: bold;")
        self.btn_toggle_subtitle.clicked.connect(self.toggle_subtitle)
        btn_row.addWidget(self.btn_toggle_subtitle, 1)

        ctrl_layout.addLayout(btn_row)
        main_layout.addWidget(ctrl_box)

        # 4. 实时日志窗口
        log_box = QGroupBox("📝 传输流水与延迟日志")
        log_layout = QVBoxLayout(log_box)
        self.txt_log = QTextEdit()
        self.txt_log.setReadOnly(True)
        log_layout.addWidget(self.txt_log)
        main_layout.addWidget(log_box, 1)

        # 初始加载预设
        self.on_provider_changed(0)
        self.append_log("系统已就绪。已自动按硬件驱动合并麦克风，杜绝重复设备。")

    def on_provider_changed(self, idx):
        provider_name = self.combo_provider.currentText()
        preset = PROVIDER_PRESETS.get(provider_name, {})
        self.txt_base_url.setText(preset.get("base_url", ""))
        self.txt_api_key.setPlaceholderText(preset.get("hint", ""))
        self.combo_model.clear()
        for m in preset.get("models", []):
            self.combo_model.addItem(m)

    def load_devices(self):
        """加载去重过滤后的系统声卡设备"""
        devices = self.router.get_devices()

        self.combo_mic.clear()
        self.combo_cable.clear()
        self.combo_monitor.clear()

        # 填充麦克风
        for d in devices["inputs"]:
            self.combo_mic.addItem(d['name'], d['id'])

        # 填充输出设备
        cable_idx = 0
        for i, d in enumerate(devices["outputs"]):
            self.combo_cable.addItem(d['name'], d['id'])
            self.combo_monitor.addItem(d['name'], d['id'])
            if devices["vb_cable_input_id"] == d['id']:
                cable_idx = i

        # 默认选中 VB-CABLE
        if devices["vb_cable_input_id"] is not None:
            self.combo_cable.setCurrentIndex(cable_idx)
            self.append_log(f"已自动绑定虚拟声卡: CABLE Input (ID: {devices['vb_cable_input_id']})")
        else:
            self.append_log("【提示】未检测到 VB-CABLE，若需将声音推给会议，请先安装虚拟声卡。")

    def toggle_subtitle(self):
        if self.subtitle_win.isVisible():
            self.subtitle_win.hide()
        else:
            self.subtitle_win.show()

    def start_ptt(self):
        self.is_recording = True
        self.btn_ptt.setText("🔴 正在录音... (松开发送并用英语推流)")
        self.status_label.setText("● 录音中")
        self.status_label.setStyleSheet("color: #ef4444; font-weight: bold;")
        
        mic_id = self.combo_mic.currentData()
        self.router.start_recording(mic_id)
        self.append_log("开始录音...")

    def stop_ptt(self):
        if not self.is_recording:
            return
        self.is_recording = False
        self.btn_ptt.setText("⏳ 处理中...")
        self.btn_ptt.setEnabled(False)

        threading.Thread(target=self._process_voice_pipeline, daemon=True).start()

    def _process_voice_pipeline(self):
        start_time = time.time()
        try:
            # 1. 获取录音
            wav_bytes = self.router.stop_recording()
            if not wav_bytes or len(wav_bytes) < 1800:
                self.signals.log.emit("录音时间太短，已忽略。")
                self._reset_ptt_btn()
                return

            api_key = self.txt_api_key.text().strip()
            base_url = self.txt_base_url.text().strip()
            model = self.combo_model.currentText().strip()
            voice = self.combo_voice.currentText().split()[0]

            self.stt.update_config(api_key, base_url)
            self.translator.update_config(api_key, base_url, model)
            self.tts.update_voice(voice)

            # 2. STT 语音识别
            self.signals.status.emit("● STT 识别中")
            t_stt = time.time()
            recognized_text = self.stt.transcribe(wav_bytes, language="zh")
            stt_cost = int((time.time() - t_stt) * 1000)
            self.signals.log.emit(f"🗣️ 识别文本: {recognized_text} (耗时: {stt_cost}ms)")

            if not recognized_text or recognized_text.startswith("["):
                self.signals.log.emit(f"⚠️ STT 识别失败: {recognized_text}")
                self._reset_ptt_btn()
                return

            # 3. 翻译为地道外企口语
            self.signals.status.emit("● LLM 翻译中")
            t_mt = time.time()
            english_text = self.translator.translate_to_english(recognized_text)
            mt_cost = int((time.time() - t_mt) * 1000)

            # 重点拦截：若翻译报错，绝不能念出报错提示
            if not english_text or english_text.startswith("[") or "Error code:" in english_text:
                self.signals.log.emit(f"❌ 翻译报错: {english_text}")
                self.signals.log.emit("👉 请检查 API Key 与 Base URL 是否匹配，避免 404 模型未找到。")
                self.signals.status.emit("● 翻译报错，已中断")
                self._reset_ptt_btn()
                return

            self.signals.log.emit(f"🌐 翻译结果: {english_text} (耗时: {mt_cost}ms)")
            self.signals.subtitle_update.emit(f"You (Zh): {recognized_text}", f"You (En): {english_text}")

            # 4. 英文语音合成
            self.signals.status.emit("● TTS 音频生成中")
            t_tts = time.time()
            english_audio = self.tts.synthesize(english_text)
            tts_cost = int((time.time() - t_tts) * 1000)

            if not english_audio:
                self.signals.log.emit("⚠️ TTS 音频合成失败。")
                self._reset_ptt_btn()
                return

            # 5. 推流发声
            cable_id = self.combo_cable.currentData()
            monitor_id = self.combo_monitor.currentData()

            total_latency = int((time.time() - start_time) * 1000)
            self.signals.log.emit(f"🔊 推流发声... [总延迟: {total_latency}ms (STT:{stt_cost}ms | MT:{mt_cost}ms | TTS:{tts_cost}ms)]")
            self.signals.status.emit("● 正在播报英文")

            self.router.play_audio(english_audio, target_device_id=cable_id, local_monitor_id=monitor_id)

        except Exception as e:
            self.signals.log.emit(f"[管道异常]: {str(e)}")
        finally:
            self._reset_ptt_btn()

    def _reset_ptt_btn(self):
        self.btn_ptt.setText("🎙️ 按住说话 (说中文 -> 自动转英文发声)")
        self.btn_ptt.setEnabled(True)
        self.status_label.setText("● 就绪")
        self.status_label.setStyleSheet("color: #10b981; font-weight: bold;")

    def append_log(self, text: str):
        timestamp = time.strftime("%H:%M:%S")
        self.txt_log.append(f"[{timestamp}] {text}")

    def update_status(self, text: str):
        self.status_label.setText(text)

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
