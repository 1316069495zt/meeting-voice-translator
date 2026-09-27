# 🎙️ Meeting Voice Copilot (外企双向实时音译电台)

> 消除语言壁垒的实时会议双向互译桌面工具：
> **听到的英文会议语音 -> 实时桌面透明中文字幕**；
> **你说的中文 -> 极速转译为专业程序员口语英文并推送到会议麦克风（让面试官听到标准英文发声）**。

---

## 🌟 核心功能

1. **出站语音变声推流 (说话中文 -> 英文发声)**：
   - 按住按键或点击说话，支持流式识别中文技术术语。
   - 大模型极速转化为自然、地道的外企技术英语。
   - 微软神经网络超逼真音色合成（男声/女声可选）。
   - 直接注入虚拟声卡（VB-CABLE），无缝伪装成硬件麦克风输出给 **Google Meet / Zoom / Microsoft Teams**。
2. **入站实时双语字幕 (英文原声 -> 中文字幕)**：
   - 桌面无边框半透明置顶字幕条，可拖拽悬浮在浏览器或摄像头画面下方。
   - 彻底摆脱英文听力焦虑，不错过面试官提出的任何技术细节。
3. **本地低延迟耳机监听**：
   - 英文音频发送给会议的同时，耳机可同步听到，掌控感拉满。
4. **全自动化云编译**：
   - 内置 GitHub Actions，代码提交自动编译生成 Windows 独立 `.exe` 安装包。

---

## 📐 系统音频拓扑

```
【入站：听英文】
浏览器 (Google Meet / Zoom) 播放对方英语
       ↓
系统扬声器正常播放（你听到） + 桌面悬浮窗实时显示中英文字幕


【出站：说中文变英文】
你对着物理麦克风说中文
       ↓
[STT 语音识别] → [LLM 极速技术英文转译] → [TTS 英文音频合成]
       ↓
写入【CABLE Input (虚拟声卡)】
       ↓
浏览器会议麦克风选择【CABLE Output】 → 对方听到标准专业英文发声
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

---

## ⚙️ API 配置建议（极致榨干延迟）

在软件界面中配置以下参数可实现最佳响应速度：

| 配置项 | 推荐填法 | 说明 |
| :--- | :--- | :--- |
| **API Key** | 你的 Key | 支持 OpenAI / DeepSeek / SiliconFlow / Groq |
| **Base URL** | `https://api.deepseek.com` | DeepSeek-V3 响应极快且成本极低 |
| **翻译模型** | `deepseek-chat` 或 `gpt-4o-mini` | 首字吐出约 200~300ms |
| **英文音色** | `en-US-ChristopherNeural` | 稳重大气的科技男声；女声可选 `en-US-JennyNeural` |

---

## 💡 远程工作与面试实用建议

1. **消除杂音**：物理麦克风只对准你自己，软件内置了防抖和空白录音过滤。
2. **坦诚加分技巧**：在开场时主动说明：“*I'm using an AI real-time translation copilot that I developed to assist our bilingual communication.*” 这不仅不是欺骗，反而能向面试官直接证明你极强的 AI 工程实践与动手能力！
3. **保持连贯性**：建议采用“按键说话”模式，按住说话，松开即刻发射。
