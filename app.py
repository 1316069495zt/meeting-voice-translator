# -*- coding: utf-8 -*-
import sys
import threading
import time
import os
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QComboBox, QLineEdit, QTextEdit,
    QGroupBox, QCheckBox, QMessageBox, QRadioButton, QButtonGroup
)
from PySide6.QtCore import Qt, Signal, QObject
from PySide6.QtGui import QFont, QIcon

from core.audio_router import AudioRouter
from core.stt_engine import STTEngine
from core.translator import Translator
from core.tts_engine import TTSEngine
from core.languages import LANGUAGE_CONFIGS
from core.config_manager import ConfigManager
from core.session_recorder import SessionRecorder
from core.hotkey import GlobalHotkeyWorker
from ui.subtitle_window import SubtitleWindow

PROVIDER_PRESETS = {
    "Groq (免费极速·推荐)": {
        "base_url": "https://api.groq.com/openai/v1",
        "models": ["qwen/qwen3.8-27b", "openai/gpt-oss-120b", "openai/gpt-oss-20b", "llama-3.3-70b-versatile"],
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
        "hint": "填入 DeepSeek 的 sk-... 密钥"
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
    reset_ptt = Signal()
    summary_done = Signal(str)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Meeting Voice Copilot (外企全双工音译电台 v1.2)")
        self.resize(920, 780)

        # 1. 配置持久化与核心模块初始化
        self.config = ConfigManager()
        self.router = AudioRouter()
        self.stt = STTEngine()
        self.translator = Translator()
        self.tts = TTSEngine()

        # 2. 会议黑匣子归档系统
        target_lang = self.config.get("target_language", "🇺🇸 英语 (English)")
        self.recorder = SessionRecorder(target_lang_name=target_lang)

        # 3. 悬浮字幕与信号系统
        self.subtitle_win = SubtitleWindow()
        self.signals = WorkerSignals()
        self.signals.log.connect(self.append_log)
        self.signals.status.connect(self.update_status)
        self.signals.subtitle_update.connect(self.subtitle_win.update_subtitles)
        self.signals.reset_ptt.connect(self._reset_ptt_btn)
        self.signals.summary_done.connect(self._on_summary_done)

        self.is_recording = False
        self.last_wav_bytes = None

        # 4. 全局快捷键监听线程 (默认 F8)
        self.hotkey_worker = GlobalHotkeyWorker(key_name=self.config.get("global_hotkey", "F8"))
        self.hotkey_worker.triggered.connect(self.on_hotkey_triggered)
        self.hotkey_worker.start()

        self.init_ui()
        self.load_devices()
        self.restore_config_to_ui()

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
            QRadioButton, QCheckBox {
                color: #e2e8f0;
                font-size: 13px;
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
        
        self.hotkey_badge = QLabel(f"⚡ 全局热键: [{self.config.get('global_hotkey', 'F8')}]")
        self.hotkey_badge.setStyleSheet("color: #f59e0b; background-color: #1e293b; border: 1px solid #b45309; border-radius: 4px; padding: 3px 8px; font-weight: bold; font-size: 11px;")
        
        self.status_label = QLabel("● 就绪")
        self.status_label.setStyleSheet("color: #10b981; font-size: 13px; font-weight: bold;")
        
        header_layout.addWidget(title_label)
        header_layout.addSpacing(10)
        header_layout.addWidget(self.hotkey_badge)
        header_layout.addStretch()
        header_layout.addWidget(self.status_label)
        main_layout.addLayout(header_layout)

        # 1. 声卡设备路由设置
        device_box = QGroupBox("🔊 1. 音频设备路由 (VB-CABLE 虚拟麦克风通道)")
        dev_layout = QVBoxLayout(device_box)

        mic_layout = QHBoxLayout()
        mic_layout.addWidget(QLabel("物理麦克风 (你的输入):"))
        self.combo_mic = QComboBox()
        self.combo_mic.currentIndexChanged.connect(self.save_current_config)
        mic_layout.addWidget(self.combo_mic, 1)

        cable_lbl = QLabel("会议输出声卡 (传给会议):")
        self.combo_cable = QComboBox()
        self.combo_cable.currentIndexChanged.connect(self.save_current_config)
        mic_layout.addWidget(cable_lbl)
        mic_layout.addWidget(self.combo_cable, 1)
        dev_layout.addLayout(mic_layout)

        monitor_layout = QHBoxLayout()
        monitor_layout.addWidget(QLabel("耳机同步监听 (听到自己发声):"))
        self.combo_monitor = QComboBox()
        self.combo_monitor.currentIndexChanged.connect(self.save_current_config)
        monitor_layout.addWidget(self.combo_monitor, 1)

        self.chk_save_audio = QCheckBox("💾 录音存盘 (保存每轮中文原音与译文推流音频)")
        self.chk_save_audio.setChecked(self.config.get("save_audio", True))
        self.chk_save_audio.stateChanged.connect(self.save_current_config)
        monitor_layout.addWidget(self.chk_save_audio)
        dev_layout.addLayout(monitor_layout)

        main_layout.addWidget(device_box)

        # 2. AI 大模型与多语种配置
        ai_box = QGroupBox("⚙️ 2. 大模型与全语种自由切换 (支持英/日/德/法/韩/西)")
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
        self.combo_model.currentIndexChanged.connect(self.save_current_config)
        row0.addWidget(self.combo_model, 1)
        ai_layout.addLayout(row0)

        row1 = QHBoxLayout()
        row1.addWidget(QLabel("API Key:"))
        self.txt_api_key = QLineEdit()
        self.txt_api_key.setEchoMode(QLineEdit.Password)
        self.txt_api_key.textChanged.connect(self.save_current_config)
        row1.addWidget(self.txt_api_key, 1)

        row1.addWidget(QLabel("Base URL:"))
        self.txt_base_url = QLineEdit()
        self.txt_base_url.textChanged.connect(self.save_current_config)
        row1.addWidget(self.txt_base_url, 1)
        ai_layout.addLayout(row1)

        row2 = QHBoxLayout()
        row2.addWidget(QLabel("🌐 目标外语:"))
        self.combo_language = QComboBox()
        for lang_name in LANGUAGE_CONFIGS.keys():
            self.combo_language.addItem(lang_name)
        self.combo_language.currentIndexChanged.connect(self.on_language_changed)
        row2.addWidget(self.combo_language, 1)

        row2.addWidget(QLabel("🗣️ 外语音色:"))
        self.combo_voice = QComboBox()
        self.combo_voice.currentIndexChanged.connect(self.save_current_config)
        row2.addWidget(self.combo_voice, 1)
        ai_layout.addLayout(row2)

        # 术语库偏置注入
        row3 = QHBoxLayout()
        row3.addWidget(QLabel("🎯 简历/技术专有词 (防Whisper与翻译拼错):"))
        self.txt_terms = QLineEdit()
        self.txt_terms.setPlaceholderText("例: Kubernetes, CUDA, Raft, Microservices, PyTorch, Latency, Deadlock")
        self.txt_terms.textChanged.connect(self.save_current_config)
        row3.addWidget(self.txt_terms, 1)
        ai_layout.addLayout(row3)

        main_layout.addWidget(ai_box)

        # 3. 会议对讲与黑匣子归档控制台
        ctrl_box = QGroupBox("🚀 3. 会议对讲与黑匣子归档控制台")
        ctrl_layout = QVBoxLayout(ctrl_box)

        mode_row = QHBoxLayout()
        mode_row.addWidget(QLabel("对讲触发方式:"))
        self.radio_hold = QRadioButton("按住说话 (Hold to talk)")
        self.radio_toggle = QRadioButton("单击启停 (Click to toggle)")
        self.mode_group = QButtonGroup(self)
        self.mode_group.addButton(self.radio_hold)
        self.mode_group.addButton(self.radio_toggle)

        if self.config.get("ptt_mode", "hold") == "toggle":
            self.radio_toggle.setChecked(True)
        else:
            self.radio_hold.setChecked(True)

        self.radio_hold.toggled.connect(self.save_current_config)
        mode_row.addWidget(self.radio_hold)
        mode_row.addWidget(self.radio_toggle)
        mode_row.addStretch()

        self.btn_open_records = QPushButton("📁 打开本场归档目录")
        self.btn_open_records.setStyleSheet("background-color: #334155; font-size: 12px;")
        self.btn_open_records.clicked.connect(self.open_records_folder)
        mode_row.addWidget(self.btn_open_records)

        self.btn_ai_summary = QPushButton("✨ 一键生成 AI 会议复盘")
        self.btn_ai_summary.setStyleSheet("background-color: #0f766e; font-size: 12px; font-weight: bold;")
        self.btn_ai_summary.clicked.connect(self.trigger_ai_summary)
        mode_row.addWidget(self.btn_ai_summary)

        ctrl_layout.addLayout(mode_row)

        btn_row = QHBoxLayout()
        self.btn_ptt = QPushButton("🎤 按住说话 (说中文 -> 自动转外语发声)")
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
        self.btn_ptt.pressed.connect(self.on_ptt_pressed)
        self.btn_ptt.released.connect(self.on_ptt_released)
        btn_row.addWidget(self.btn_ptt, 2)

        self.btn_toggle_subtitle = QPushButton("📺 切换双语字幕悬浮窗")
        self.btn_toggle_subtitle.setStyleSheet("background-color: #6366f1; padding: 13px; font-weight: bold;")
        self.btn_toggle_subtitle.clicked.connect(self.toggle_subtitle)
        btn_row.addWidget(self.btn_toggle_subtitle, 1)

        ctrl_layout.addLayout(btn_row)
        main_layout.addWidget(ctrl_box)

        # 4. 实时日志窗口
        log_box = QGroupBox("📝 会议黑匣子实时日志流水")
        log_layout = QVBoxLayout(log_box)
        self.txt_log = QTextEdit()
        self.txt_log.setReadOnly(True)
        log_layout.addWidget(self.txt_log)
        main_layout.addWidget(log_box, 1)

        self.append_log(f"系统就绪。当前归档目录: {self.recorder.session_dir}")
        self.append_log(f"全局对讲热键已就绪: [{self.config.get('global_hotkey', 'F8')}]。开会时无需切屏，随手按键即可对讲。")

    def on_provider_changed(self, idx):
        provider_name = self.combo_provider.currentText()
        preset = PROVIDER_PRESETS.get(provider_name, {})
        self.txt_base_url.setText(preset.get("base_url", ""))
        self.txt_api_key.setPlaceholderText(preset.get("hint", ""))
        self.combo_model.clear()
        for m in preset.get("models", []):
            self.combo_model.addItem(m)
        self.save_current_config()

    def on_language_changed(self, idx):
        lang_name = self.combo_language.currentText()
        cfg = LANGUAGE_CONFIGS.get(lang_name, LANGUAGE_CONFIGS["🇺🇸 英语 (English)"])
        self.combo_voice.clear()
        for voice_id, label in cfg["voices"]:
            self.combo_voice.addItem(label, voice_id)
        self.recorder.target_lang_name = cfg["target_lang_name"]
        self.append_log(f"目标语言已切换为: {lang_name} (自动挂载专属 Prompt 与神经网络音色)")
        self.save_current_config()

    def load_devices(self):
        devices = self.router.get_devices()
        self.combo_mic.clear()
        self.combo_cable.clear()
        self.combo_monitor.clear()

        for d in devices["inputs"]:
            self.combo_mic.addItem(d['name'], d['id'])

        cable_idx = 0
        for i, d in enumerate(devices["outputs"]):
            self.combo_cable.addItem(d['name'], d['id'])
            self.combo_monitor.addItem(d['name'], d['id'])
            if devices["vb_cable_input_id"] == d['id']:
                cable_idx = i

        if devices["vb_cable_input_id"] is not None:
            self.combo_cable.setCurrentIndex(cable_idx)
            self.append_log(f"已自动绑定虚拟声卡: CABLE Input (ID: {devices['vb_cable_input_id']})")
        else:
            self.append_log("【提示】未检测到 VB-CABLE，若需将声音推给会议，请确认安装虚拟声卡。")

    def restore_config_to_ui(self):
        saved_provider = self.config.get("provider")
        if saved_provider:
            idx = self.combo_provider.findText(saved_provider)
            if idx >= 0:
                self.combo_provider.setCurrentIndex(idx)

        if self.config.get("base_url"):
            self.txt_base_url.setText(self.config.get("base_url"))
        if self.config.get("api_key"):
            self.txt_api_key.setText(self.config.get("api_key"))
        if self.config.get("model"):
            self.combo_model.setCurrentText(self.config.get("model"))
        if self.config.get("custom_terms"):
            self.txt_terms.setText(self.config.get("custom_terms"))

        saved_lang = self.config.get("target_language")
        if saved_lang:
            l_idx = self.combo_language.findText(saved_lang)
            if l_idx >= 0:
                self.combo_language.setCurrentIndex(l_idx)
        else:
            self.on_language_changed(0)

        # 恢复设备选择
        if self.config.get("mic_name"):
            m_idx = self.combo_mic.findText(self.config.get("mic_name"))
            if m_idx >= 0: self.combo_mic.setCurrentIndex(m_idx)
        if self.config.get("cable_name"):
            c_idx = self.combo_cable.findText(self.config.get("cable_name"))
            if c_idx >= 0: self.combo_cable.setCurrentIndex(c_idx)
        if self.config.get("monitor_name"):
            o_idx = self.combo_monitor.findText(self.config.get("monitor_name"))
            if o_idx >= 0: self.combo_monitor.setCurrentIndex(o_idx)

    def save_current_config(self):
        ptt_mode = "toggle" if self.radio_toggle.isChecked() else "hold"
        voice_id = self.combo_voice.currentData()
        if not voice_id:
            voice_id = "en-US-ChristopherNeural"

        self.config.save(
            provider=self.combo_provider.currentText(),
            base_url=self.txt_base_url.text().strip(),
            model=self.combo_model.currentText().strip(),
            api_key=self.txt_api_key.text().strip(),
            target_language=self.combo_language.currentText(),
            voice=voice_id,
            mic_name=self.combo_mic.currentText(),
            cable_name=self.combo_cable.currentText(),
            monitor_name=self.combo_monitor.currentText(),
            custom_terms=self.txt_terms.text().strip(),
            save_audio=self.chk_save_audio.isChecked(),
            ptt_mode=ptt_mode
        )

    def on_hotkey_triggered(self):
        """全局快捷键触发（F8）"""
        self.append_log(f"⚡ [全局热键触发]")
        if self.radio_toggle.isChecked():
            # 单击切换模式
            if self.is_recording:
                self.stop_ptt()
            else:
                self.start_ptt()
        else:
            # 持续对讲触发
            if not self.is_recording:
                self.start_ptt()
            else:
                self.stop_ptt()

    def on_ptt_pressed(self):
        if self.radio_toggle.isChecked():
            # 单击切换模式：点击一次启动，再次点击停止
            if self.is_recording:
                self.stop_ptt()
            else:
                self.start_ptt()
        else:
            # 长按模式
            self.start_ptt()

    def on_ptt_released(self):
        if not self.radio_toggle.isChecked():
            # 仅长按模式在松开时触发停止
            self.stop_ptt()

    def start_ptt(self):
        if self.is_recording:
            return
        self.is_recording = True
        self.btn_ptt.setText("🔴 正在录音... (说中文，结束自动转外语推流)")
        self.btn_ptt.setStyleSheet("background-color: #ef4444; font-size: 15px; font-weight: bold; padding: 13px;")
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
            # 1. 抓取录音
            wav_bytes = self.router.stop_recording()
            if not wav_bytes or len(wav_bytes) < 1800:
                self.signals.log.emit("录音时间太短，已忽略。")
                self.signals.reset_ptt.emit()
                return

            api_key = self.txt_api_key.text().strip()
            base_url = self.txt_base_url.text().strip()
            model = self.combo_model.currentText().strip()
            target_lang = self.combo_language.currentText()
            voice_id = self.combo_voice.currentData() or "en-US-ChristopherNeural"
            custom_terms = self.txt_terms.text().strip()

            self.stt.update_config(api_key, base_url)
            self.translator.update_config(api_key, base_url, model)
            self.tts.update_voice(voice_id)

            # 2. STT 语音识别（注入专业术语偏置）
            self.signals.status.emit("● STT 识别中")
            t_stt = time.time()
            recognized_text = self.stt.transcribe(wav_bytes, language="zh", prompt_terms=custom_terms)
            stt_cost = int((time.time() - t_stt) * 1000)
            self.signals.log.emit(f"🗣️ 识别文本: {recognized_text} (耗时: {stt_cost}ms)")

            if not recognized_text or recognized_text.startswith("["):
                self.signals.log.emit(f"⚠️ STT 识别失败: {recognized_text}")
                self.signals.reset_ptt.emit()
                return

            # 3. LLM 极速外语翻译（注入语言专属技术规范 Prompt）
            self.signals.status.emit("● LLM 翻译中")
            t_mt = time.time()
            translated_text = self.translator.translate_speech(recognized_text, target_lang, custom_terms=custom_terms)
            mt_cost = int((time.time() - t_mt) * 1000)

            if not translated_text or translated_text.startswith("[") or "Error code:" in translated_text:
                self.signals.log.emit(f"❌ 翻译报错: {translated_text}")
                self.signals.status.emit("● 翻译报错，已中断")
                self.signals.reset_ptt.emit()
                return

            self.signals.log.emit(f"🌐 翻译结果: {translated_text} (耗时: {mt_cost}ms)")
            self.signals.subtitle_update.emit(f"You (Zh): {recognized_text}", f"You ({target_lang[:2]}): {translated_text}")

            # 4. 神经网络语音合成
            self.signals.status.emit("● TTS 语音生成中")
            t_tts = time.time()
            foreign_audio = self.tts.synthesize(translated_text)
            tts_cost = int((time.time() - t_tts) * 1000)

            if not foreign_audio:
                self.signals.log.emit("⚠️ TTS 音频合成失败。")
                self.signals.reset_ptt.emit()
                return

            # 5. 会议虚拟麦克风推流与本地监听
            cable_id = self.combo_cable.currentData()
            monitor_id = self.combo_monitor.currentData()
            total_latency = int((time.time() - start_time) * 1000)

            self.signals.log.emit(f"🔊 推流发声... [总延迟: {total_latency}ms (STT:{stt_cost}ms | MT:{mt_cost}ms | TTS:{tts_cost}ms)]")
            self.signals.status.emit("● 正在播报外语")

            # 6. 会议黑匣子数据存盘
            latency_stats = {"total": total_latency, "stt": stt_cost, "mt": mt_cost, "tts": tts_cost}
            save_audio = self.chk_save_audio.isChecked()
            self.recorder.record_exchange(
                zh_text=recognized_text,
                target_text=translated_text,
                target_lang=target_lang,
                latency_stats=latency_stats,
                wav_bytes=wav_bytes,
                mp3_bytes=foreign_audio,
                save_audio=save_audio
            )

            self.router.play_audio(foreign_audio, target_device_id=cable_id, local_monitor_id=monitor_id)

        except Exception as e:
            self.signals.log.emit(f"[管道异常]: {str(e)}")
        finally:
            self.signals.reset_ptt.emit()

    def _reset_ptt_btn(self):
        mode_text = "单击说话" if self.radio_toggle.isChecked() else "按住说话"
        self.btn_ptt.setText(f"🎤 {mode_text} (说中文 -> 自动转外语发声)")
        self.btn_ptt.setStyleSheet("""
            QPushButton {
                background-color: #10b981;
                font-size: 15px;
                font-weight: bold;
                padding: 13px;
            }
            QPushButton:hover { background-color: #059669; }
        """)
        self.btn_ptt.setEnabled(True)
        self.status_label.setText("● 就绪")
        self.status_label.setStyleSheet("color: #10b981; font-weight: bold;")

    def open_records_folder(self):
        self.recorder.open_folder()
        self.append_log(f"已在资源管理器中打开归档目录: {self.recorder.session_dir}")

    def trigger_ai_summary(self):
        if not self.recorder.dialogue_history:
            QMessageBox.information(self, "提示", "当前会议暂无对话记录，请先进行对讲发声。")
            return

        self.btn_ai_summary.setEnabled(False)
        self.btn_ai_summary.setText("⏳ AI 正在复盘生成中...")
        self.append_log("✨ 正在汇总本场会议对话流并调用大模型进行技术复盘...")

        def _worker():
            api_key = self.txt_api_key.text().strip()
            base_url = self.txt_base_url.text().strip()
            model = self.combo_model.currentText().strip()
            self.translator.update_config(api_key, base_url, model)
            summary = self.recorder.generate_ai_summary(self.translator.client, model=model)
            self.signals.summary_done.emit(summary)

        threading.Thread(target=_worker, daemon=True).start()

    def _on_summary_done(self, summary_text):
        self.btn_ai_summary.setEnabled(True)
        self.btn_ai_summary.setText("✨ 一键生成 AI 会议复盘")
        self.append_log("✅ AI 会议/面试复盘已生成并存入 summary.md！")
        self.append_log("----------------- 📋 会议复盘摘要 -----------------")
        self.append_log(summary_text[:300] + ("..." if len(summary_text) > 300 else ""))
        self.append_log("---------------------------------------------------")
        QMessageBox.information(self, "AI 会议复盘生成完毕", f"已成功生成本场技术复盘总结并保存至：\n{self.recorder.summary_file}\n\n点击'打开归档目录'即可查看完整 Markdown 报告。")

    def toggle_subtitle(self):
        if self.subtitle_win.isVisible():
            self.subtitle_win.hide()
        else:
            self.subtitle_win.show()

    def append_log(self, text: str):
        timestamp = time.strftime("%H:%M:%S")
        self.txt_log.append(f"[{timestamp}] {text}")

    def update_status(self, text: str):
        self.status_label.setText(text)

    def closeEvent(self, event):
        self.save_current_config()
        if hasattr(self, 'hotkey_worker') and self.hotkey_worker.isRunning():
            self.hotkey_worker.stop()
        event.accept()

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
