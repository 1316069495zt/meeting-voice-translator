# -*- coding: utf-8 -*-
import sys
import threading
import time
from PySide6.QtCore import QThread, Signal

class GlobalHotkeyWorker(QThread):
    """
    Windows 原生低延迟全局快捷键监听器：
    利用 ctypes 调用 Win32 API (RegisterHotKey)，零额外三方包依赖，
    彻底解决面试时全屏看代码/PPT无法按对讲键的问题。
    """
    triggered = Signal()

    def __init__(self, key_name="F8", parent=None):
        super().__init__(parent)
        self.key_name = key_name
        self.running = True
        self.hotkey_id = 9999

        # VK 虚拟键码映射表
        self.vk_map = {
            "F8": 0x77,
            "F7": 0x76,
            "F9": 0x78,
            "F10": 0x79,
            "PAUSE": 0x13,
            "SCROLL_LOCK": 0x91
        }

    def run(self):
        if sys.platform != "win32":
            return

        import ctypes
        from ctypes import wintypes

        user32 = ctypes.windll.user32
        vk = self.vk_map.get(self.key_name.upper(), 0x77) # 默认 F8
        MOD_NOREPEAT = 0x4000

        # 注册全局热键
        if not user32.RegisterHotKey(None, self.hotkey_id, MOD_NOREPEAT, vk):
            print(f"[Hotkey] 注册全局快捷键 {self.key_name} 失败 (可能被占用)")
            return

        print(f"[Hotkey] 全局快捷键 [{self.key_name}] 已成功挂载")
        msg = wintypes.MSG()

        try:
            while self.running:
                # 使用 PeekMessage 避免死锁并允许优雅退出
                if user32.PeekMessageW(ctypes.byref(msg), None, 0, 0, 1):
                    if msg.message == 0x0312: # WM_HOTKEY
                        if msg.wParam == self.hotkey_id:
                            self.triggered.emit()
                    user32.TranslateMessage(ctypes.byref(msg))
                    user32.DispatchMessageW(ctypes.byref(msg))
                else:
                    time.sleep(0.02)
        finally:
            user32.UnregisterHotKey(None, self.hotkey_id)
            print(f"[Hotkey] 全局快捷键 [{self.key_name}] 已安全卸载")

    def stop(self):
        self.running = False
        self.wait(1000)
