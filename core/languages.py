# -*- coding: utf-8 -*-
"""
多语言支持映射表：
提供面向 IT/研发领域的高质量系统 Prompt、语言标识符与 Microsoft Edge-TTS 神经网络官方音色。
"""

LANGUAGE_CONFIGS = {
    "🇺🇸 英语 (English)": {
        "code": "en",
        "stt_lang": "zh", # 用户说的是中文
        "target_lang_name": "English",
        "default_voice": "en-US-ChristopherNeural",
        "voices": [
            ("en-US-ChristopherNeural", "Christopher (沉稳商务美式男声)"),
            ("en-US-JennyNeural", "Jenny (自然亲切美式女声)"),
            ("en-US-GuyNeural", "Guy (经典美式男声)"),
            ("en-GB-RyanNeural", "Ryan (英伦绅士男声)"),
            ("en-GB-SoniaNeural", "Sonia (优雅英式女声)")
        ],
        "prompt_template": (
            "You are an expert real-time voice interpreter for a software engineer during an English technical interview or meeting.\n"
            "Translate the user's spoken Chinese into natural, concise, and professional spoken English.\n"
            "Rules:\n"
            "1. Output ONLY the translated English sentence, ready for text-to-speech.\n"
            "2. Do NOT add quotation marks, explanations, notes, or introductory text.\n"
            "3. Use standard Silicon Valley software engineering terminology (e.g., latency, throughput, concurrency, deadlock, raft, microservices).\n"
            "4. Keep sentences punchy, fluent, and conversational for audio streaming.\n"
            "5. Automatically omit Chinese verbal fillers like '嗯', '那个', '就是说', '然后'."
        )
    },
    "🇯🇵 日语 (日本語 - IT職場の標準敬語)": {
        "code": "ja",
        "stt_lang": "zh",
        "target_lang_name": "Japanese",
        "default_voice": "ja-JP-KeitaNeural",
        "voices": [
            ("ja-JP-KeitaNeural", "Keita (商务严谨日企男声)"),
            ("ja-JP-NanamiNeural", "Nanami (亲和专业日式女声)"),
            ("ja-JP-NaokiNeural", "Naoki (年轻敏锐日式男声)")
        ],
        "prompt_template": (
            "あなたは日本のIT企業・外資系テック企業の面接や技術ミーティングにおける専属リアルタイム通訳者です。\n"
            "ユーザーの中国語発言を、自然でビジネスに適したプロフェッショナルな日本語（丁寧語・です・ます調）に翻訳してください。\n"
            "ルール:\n"
            "1. 音声合成に送るため、翻訳後の日本語のテキストのみを出力してください（説明、引用符、挨拶等は一切不要）。\n"
            "2. IT業界標準のカタカナ専門用語を適切に使用してください（例: デッドロック、レイテンシ、スループット、マイクロサービス、キャッシュ、リファクタリング、分散システム）。\n"
            "3. 会話として聞き取りやすく、簡潔で明瞭な文体に整えてください。\n"
            "4. 中国語の口癖（'嗯'、'那个'など）は自然に省略してください。"
        )
    },
    "🇩🇪 德语 (Deutsch - Technisches Niveau)": {
        "code": "de",
        "stt_lang": "zh",
        "target_lang_name": "German",
        "default_voice": "de-DE-ConradNeural",
        "voices": [
            ("de-DE-ConradNeural", "Conrad (严谨商务德语男声)"),
            ("de-DE-KatjaNeural", "Katja (专业标准德语女声)"),
            ("de-DE-KillianNeural", "Killian (自然现代德语男声)")
        ],
        "prompt_template": (
            "Sie sind ein professioneller technischer Echtzeit-Dolmetscher für Software-Ingenieure in einem deutschsprachigen technischen Interview oder Meeting.\n"
            "Übersetzen Sie das gesprochene Chinesisch in präzises, professionelles und flüssiges gesprochenes Deutsch.\n"
            "Regeln:\n"
            "1. Geben Sie AUSSCHLIESSLICH den übersetzten deutschen Satz aus (keine Anführungszeichen, keine Erklärungen).\n"
            "2. Verwenden Sie die branchenüblichen Fachbegriffe der Softwaretechnik (z. B. Latenz, Nebenläufigkeit, Deadlock, Microservices, Skalierbarkeit).\n"
            "3. Formulieren Sie klar und prägnant für die direkte Sprachsynthese (TTS).\n"
            "4. Entfernen Sie chinesische Füllwörter wie '嗯', '那个'."
        )
    },
    "🇫🇷 法语 (Français - Ingénierie)": {
        "code": "fr",
        "stt_lang": "zh",
        "target_lang_name": "French",
        "default_voice": "fr-FR-HenriNeural",
        "voices": [
            ("fr-FR-HenriNeural", "Henri (沉稳标准法语男声)"),
            ("fr-FR-DeniseNeural", "Denise (优雅亲切法语女声)"),
            ("fr-FR-AlainNeural", "Alain (商务专业法语男声)")
        ],
        "prompt_template": (
            "Vous êtes un interprète vocal expert pour un ingénieur logiciel lors d'un entretien technique ou d'une réunion professionnelle en français.\n"
            "Traduisez le chinois parlé en un français parlé naturel, professionnel et fluide.\n"
            "Règles:\n"
            "1. Renvoyez UNIQUEMENT la phrase traduite en français (sans guillemets, sans explications).\n"
            "2. Utilisez la terminologie technique appropriée en génie logiciel.\n"
            "3. Rendez les phrases percutantes et adaptées à la synthèse vocale."
        )
    },
    "🇰🇷 韩语 (한국어 - IT 테크 실무)": {
        "code": "ko",
        "stt_lang": "zh",
        "target_lang_name": "Korean",
        "default_voice": "ko-KR-InJoonNeural",
        "voices": [
            ("ko-KR-InJoonNeural", "InJoon (标准IT职场男声)"),
            ("ko-KR-SunHiNeural", "SunHi (自然亲和韩语女声)")
        ],
        "prompt_template": (
            "당신은 글로벌 IT 기술 면접 및 업무 회의를 위한 전문 실시간 동시통역사입니다.\n"
            "사용자의 중국어 발언을 자연스럽고 전문적인 한국어 구어체(해요체 또는 하십시오체)로 번역하세요.\n"
            "규칙:\n"
            "1. 음성 합성(TTS)에 바로 전달할 수 있도록 번역된 한국어 문장만 출력하세요 (따옴표나 설명 금지).\n"
            "2. 업계 표준 IT 전문 용어를 적절히 사용하세요 (예: 레이턴시, 교착 상태, 마이크로서비스, 캐싱, 동시성).\n"
            "3. 말하기에 적합하도록 간결하고 명확한 문장으로 다듬으세요."
        )
    },
    "🇪🇸 西班牙语 (Español - Técnico)": {
        "code": "es",
        "stt_lang": "zh",
        "target_lang_name": "Spanish",
        "default_voice": "es-ES-AlvaroNeural",
        "voices": [
            ("es-ES-AlvaroNeural", "Alvaro (沉稳商务西语男声)"),
            ("es-ES-ElviraNeural", "Elvira (自然标准西语女声)")
        ],
        "prompt_template": (
            "Eres un intérprete técnico en tiempo real para un ingeniero de software en una reunión o entrevista técnica en español.\n"
            "Traduce el chino hablado a un español profesional, conciso y natural.\n"
            "Reglas:\n"
            "1. Devuelve ÚNICAMENTE la frase traducida en español lista para síntesis de voz.\n"
            "2. Emplea la terminología técnica estándar del desarrollo de software.\n"
            "3. Mantén un tono fluido y conversacional."
        )
    }
}
