from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QPushButton
from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QFont, QColor

class SubtitleWindow(QWidget):
    """
    桌面悬浮透明置顶字幕窗口：
    显示会议中捕获到的英文与实时中文翻译。可随意拖动放置在会议软件上方。
    """
    def __init__(self):
        super().__init__()
        self.drag_position = QPoint()

        # 窗口属性：无边框、置顶、半透明
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.resize(750, 140)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 10, 15, 10)

        # 容器背景框
        container = QWidget()
        container.setStyleSheet("""
            QWidget {
                background-color: rgba(15, 23, 42, 220);
                border: 1px solid rgba(56, 189, 248, 120);
                border-radius: 12px;
            }
        """)
        c_layout = QVBoxLayout(container)
        c_layout.setContentsMargins(12, 8, 12, 8)

        # 顶部小标题栏
        top_bar = QHBoxLayout()
        title = QLabel("📡 会议双语字幕悬浮窗 (按住可拖动)")
        title.setStyleSheet("color: #94a3b8; font-size: 11px; border: none; background: transparent;")
        
        btn_close = QPushButton("✕")
        btn_close.setFixedSize(20, 20)
        btn_close.setStyleSheet("""
            QPushButton {
                background: transparent; color: #94a3b8; border: none; font-size: 12px; font-weight: bold;
            }
            QPushButton:hover {
                color: #ef4444;
            }
        """)
        btn_close.clicked.connect(self.hide)

        top_bar.addWidget(title)
        top_bar.addStretch()
        top_bar.addWidget(btn_close)
        c_layout.addLayout(top_bar)

        # 原文显示（英）
        self.lbl_source = QLabel("等待接收会议英文语音...")
        self.lbl_source.setStyleSheet("color: #cbd5e1; font-size: 13px; font-family: 'Segoe UI', sans-serif; border: none; background: transparent;")
        self.lbl_source.setWordWrap(True)
        c_layout.addWidget(self.lbl_source)

        # 译文显示（中，高亮醒目）
        self.lbl_target = QLabel("中文字幕将在此实时呈现")
        self.lbl_target.setStyleSheet("color: #38bdf8; font-size: 16px; font-weight: bold; font-family: 'Microsoft YaHei', sans-serif; border: none; background: transparent;")
        self.lbl_target.setWordWrap(True)
        c_layout.addWidget(self.lbl_target)

        layout.addWidget(container)

    def update_subtitles(self, source_text: str, target_text: str):
        """更新字幕内容"""
        self.lbl_source.setText(source_text if source_text else "...")
        self.lbl_target.setText(target_text if target_text else "...")

    # 鼠标拖拽移动窗口逻辑
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()
