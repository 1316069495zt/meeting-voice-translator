# -*- coding: utf-8 -*-
import os
import sys
import time
import json
import subprocess

class SessionRecorder:
    """
    会议黑匣子与专属文件夹归档系统：
    1. 自动为每次会话/会议建立独立时间戳目录 (records/YYYY-MM-DD_HH-MM-SS)；
    2. 实时生成美观排版的双语对齐时间轴 Markdown (transcript.md)；
    3. 支持保存输入 WAV 与翻译推流 MP3 音频留痕；
    4. 会后一键 AI 智能复盘提炼纪要 (summary.md)；
    5. 一键在 Windows 资源管理器中打开当前归档目录。
    """
    def __init__(self, target_lang_name="English"):
        if getattr(sys, 'frozen', False):
            base_dir = os.path.dirname(sys.executable)
        else:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        self.records_root = os.path.join(base_dir, "records")
        os.makedirs(self.records_root, exist_ok=True)

        # 当前会话目录
        self.session_id = time.strftime("%Y-%m-%d_%H-%M-%S")
        self.session_dir = os.path.join(self.records_root, self.session_id)
        self.audio_dir = os.path.join(self.session_dir, "audio")
        os.makedirs(self.audio_dir, exist_ok=True)

        self.transcript_file = os.path.join(self.session_dir, "transcript.md")
        self.summary_file = os.path.join(self.session_dir, "summary.md")
        self.target_lang_name = target_lang_name

        self.dialogue_history = []
        self.counter = 0

        self._init_transcript()

    def _init_transcript(self):
        header = (
            f"# 🎙️ 会议对讲双语纪要 (Session: {self.session_id})\n\n"
            f"> **开始时间**：{time.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"> **目标语言**：{self.target_lang_name}\n"
            f"> **归档目录**：`{self.session_dir}`\n\n"
            f"---\n\n"
            f"| 时间 | 序号 | 🗣️ 原始中文发言 | 🌐 译文推流 ({self.target_lang_name}) | ⏱️ 时延 (STT/MT/TTS) |\n"
            f"| :--- | :--- | :--- | :--- | :--- |\n"
        )
        try:
            with open(self.transcript_file, "w", encoding="utf-8") as f:
                f.write(header)
        except Exception as e:
            print(f"[SessionRecorder] 初始化文件异常: {e}")

    def record_exchange(self, zh_text: str, target_text: str, target_lang: str,
                        latency_stats: dict, wav_bytes: bytes = None, mp3_bytes: bytes = None,
                        save_audio: bool = True):
        """
        实时记录一次发言片段
        """
        self.counter += 1
        now_str = time.strftime("%H:%M:%S")

        # 音频落盘
        audio_ref = "-"
        if save_audio:
            in_audio_name = f"{self.counter:03d}_zh.wav"
            out_audio_name = f"{self.counter:03d}_{target_lang.lower()[:2]}.mp3"
            
            in_path = os.path.join(self.audio_dir, in_audio_name)
            out_path = os.path.join(self.audio_dir, out_audio_name)

            if wav_bytes:
                try:
                    with open(in_path, "wb") as f:
                        f.write(wav_bytes)
                except Exception:
                    pass

            if mp3_bytes:
                try:
                    with open(out_path, "wb") as f:
                        f.write(mp3_bytes)
                except Exception:
                    pass

            audio_ref = f"[原音](audio/{in_audio_name}) / [推流](audio/{out_audio_name})"

        # 整理统计指标
        total_lat = latency_stats.get("total", 0)
        stt_lat = latency_stats.get("stt", 0)
        mt_lat = latency_stats.get("mt", 0)
        tts_lat = latency_stats.get("tts", 0)
        lat_str = f"{total_lat}ms ({stt_lat}/{mt_lat}/{tts_lat})"

        # 清洗表格中的换行
        clean_zh = zh_text.replace("\n", " ").replace("|", "\\|")
        clean_target = target_text.replace("\n", " ").replace("|", "\\|")

        row = f"| {now_str} | #{self.counter:02d} | {clean_zh} | {clean_target} | {lat_str} |\n"

        try:
            with open(self.transcript_file, "a", encoding="utf-8") as f:
                f.write(row)
        except Exception as e:
            print(f"[SessionRecorder] 写入对讲记录失败: {e}")

        # 缓存供会后 AI 复盘总结
        self.dialogue_history.append({
            "index": self.counter,
            "time": now_str,
            "zh": zh_text,
            "foreign": target_text
        })

    def generate_ai_summary(self, translator_client, model="deepseek-chat") -> str:
        """
        调用大模型生成专业的会议技术复盘与待办事项总结
        """
        if not self.dialogue_history:
            return "本场会话暂无发言记录，无需生成复盘。"

        # 拼接全部对话记录
        convo_text = ""
        for item in self.dialogue_history:
            convo_text += f"[{item['time']}] 用户中文: {item['zh']}\n翻译输出: {item['foreign']}\n\n"

        prompt = (
            "你是一个外企高级技术主管和职业技术面试官助理。以下是候选人/工程师在一次英文技术面试/会议中的全量双语发言流水：\n\n"
            f"{convo_text}\n"
            "请根据上述实际发言，生成一份结构清晰、高度专业的《会议与面试技术复盘报告》(Markdown格式)，包含：\n"
            "1. 【会议/面试核心议题与技术场景概览】(Brief Overview)\n"
            "2. 【讨论的核心技术栈与关键技术回答梳理】(Technical Highlights & Topics Covered)\n"
            "3. 【表达与回答表现复盘】(回答亮点、可以表达得更精准或更深入的技术建议)\n"
            "4. 【会后待办事项与跟进清单】(Action Items & Commitments)\n"
            "请使用清晰优雅的中文进行排版，重要技术术语保留原汁原味的英文。"
        )

        try:
            resp = translator_client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a professional engineering manager and technical interviewer."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            summary_content = resp.choices[0].message.content.strip()

            # 存盘
            full_md = (
                f"# 📋 会议/面试智能技术复盘报告\n\n"
                f"> **会话编号**：`{self.session_id}`\n"
                f"> **生成时间**：{time.strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"> **对话片段数**：共 {len(self.dialogue_history)} 段\n\n"
                f"---\n\n"
                f"{summary_content}\n"
            )
            with open(self.summary_file, "w", encoding="utf-8") as f:
                f.write(full_md)

            return summary_content
        except Exception as e:
            err_msg = f"生成会议复盘失败: {e}"
            print(f"[SessionRecorder] {err_msg}")
            return err_msg

    def open_folder(self):
        """在 Windows 资源管理器中打开当前会话归档目录"""
        try:
            if sys.platform == "win32":
                os.startfile(self.session_dir)
            else:
                subprocess.Popen(["explorer.exe", self.session_dir.replace("/", "\\")])
        except Exception as e:
            print(f"[SessionRecorder] 打开文件夹失败: {e}")
