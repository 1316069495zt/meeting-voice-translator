# 🎙️ Meeting Voice Copilot (外企双向实时音译电台 v1.2)

> 消除语言壁垒的实时会议双向互译桌面工具：
> **听到的外语会议语音 -> 实时桌面透明中文字幕**；
> **你说的中文 -> 极速转译为专业程序员口语外语（英语/日语/德语/法语/韩语/西语）并推送到会议麦克风（让面试官听到标准外语发声）**。

---

## 🌟 核心功能

1. **出站语音变声推流 (说话中文 -> 多外语发声)**：
   - **全语种支持**：自由切换英语 (美/英)、日语 (ITビジネス・丁寧語)、德语、法语、韩语、西班牙语。
   - **大模型极速转译**：基于 Groq (Qwen 3.8 27B / Llama 3.3) 或 DeepSeek / OpenAI，百毫秒级转译为自然、地道的技术外语。
   - **简历技术术语库偏置**：支持注入专有名词（如 CUDA, K8s, Raft, Microservices），Whisper 与大模型协同防止专业缩写拼错。
   - **微软神经网络超逼真音色**：针对各语种深度适配官方顶级原生 Neural 音色。
   - **无缝伪装硬件麦克风**：写入虚拟声卡（VB-CABLE），输出给 **Google Meet / Zoom / Microsoft Teams**。
2. **会议黑匣子与文件夹归档系统**：
   - 自动在 `records/` 下建立以时间戳命名的独立会议目录。
   - 实时生成对齐排版的 **`transcript.md`**（时间轴、中文发言、外语推流、各环节耗时毫秒级分解）。
   - **音频原声存盘**：可选自动保留中文原声 WAV 与外语推流 MP3。
   - **✨ 一键 AI 会议复盘总结**：点击按钮自动由大模型分析整场发言，生成核心技术议题、回答表现复盘与 Action Items 待办清单并存入 `summary.md`。
   - **📁 一键打开归档目录**：界面直通 Windows 资源管理器。
3. **全局免切屏对讲与双模式触发**：
   - **全局热键（默认 F8）**：面试全屏看代码、看 PPT 或看简历时无需切屏，随手按键即可对讲。
   - **双模式自由切换**：支持“长按说话（Hold）”与“单击启停（Toggle）”模式。
4. **配置自动持久化**：
   - 自动保存 API Key、Base URL、所选麦克风/耳机、目标语言与术语表至 `config.json`，下次启动秒级就绪。
5. **入站实时双语字幕**：
   - 桌面无边框半透明置顶字幕条，可拖拽悬浮在浏览器或摄像头画面下方。
6. **本地低延迟耳机监听**：
   - 外语音频发送给会议的同时，耳机可同步听到，掌控感拉满。
7. **全自动化云编译**：
   - 内置 GitHub Actions，代码提交自动编译生成 Windows 独立 `.exe` 安装包。

---

## 📐 系统音频拓扑

```
【你在说话】
你对着物理麦克风说中文
       ↓
[STT 语音识别 (带术语库偏置)] → [LLM 极速技术外语转译] → [TTS 官方神经音色合成]
       ↓
【双路推流】
  ├─→ 写入【CABLE Input (虚拟声卡)】 ─→ 浏览器会议麦克风选择【CABLE Output】 ─→ 对方听到纯正外语发声
  ├─→ 写入【你的耳机 (本地监听)】 ─→ 实时掌握自己发出的声音
  └─→ 写入【records/ 会议黑匣子】 ─→ transcript.md 实时速记与录音归档
```

---

## 🚀 快速上手

### 必备前置：安装免费虚拟声卡 (VB-CABLE)
1. 前往 [VB-Audio 官网](https://vb-audio.com/Cable/) 下载 **VB-CABLE Driver**（Windows版）。
2. 解压并以管理员身份运行 `VBCABLE_Setup_x64.exe` 完成安装，重启电脑。
3. **浏览器会议设置**：
   - 进入 Google Meet / Zoom / Teams 的音频设置。
   - **麦克风（Microphone）** 选择：`CABLE Output (VB-Audio Virtual Cable)`。

---

### 获取 Windows 运行程序（两种方式）

#### 方式一：直接在 GitHub Actions 下载编译好的 exe（推荐）
1. 在当前 GitHub 仓库顶部点击 **Actions** 标签页。
2. 点击最新的构建工作流 **Build Windows Executable**。
3. 在页面下方 **Artifacts** 处下载 `MeetingVoiceCopilot-Windows-x64.zip`。
4. 解压后双击 `MeetingVoiceCopilot.exe` 即可直接运行，免装 Python 环境！

#### 方式二：本地源码运行与编译
需要本地安装 Python 3.10+：

```bash
# 1. 克隆仓库
git clone https://github.com/1316069495zt/meeting-voice-translator.git
cd meeting-voice-translator

# 2. 安装依赖
pip install -r requirements.txt

# 3. 运行程序
python app.py

# 4. (可选) 本地一键打包为 EXE
双击运行 build_exe.bat
```
