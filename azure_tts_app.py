import os
import subprocess
import re
from datetime import datetime

import streamlit as st
import azure.cognitiveservices.speech as speechsdk
import streamlit.components.v1 as components
import base64


YOUTUBE_DESCRIPTION_TEMPLATES = {
    # 一般德文聽力 / 閱讀 / 口語跟讀
    "general_listening": """#Deutschlernen #GermanListening #TELC #Deutschverstehen
📌 Deutsche Hörübung – Vorlesen eines Übungstextes zur Prüfungsvorbereitung

In diesem Video wird ein deutscher Übungstext langsam, deutlich und mit natürlicher Betonung vorgelesen. Ideal für:
✓ Vorbereitung auf TestDaF / DSH / Goethe / TELC
✓ Training des Hörverstehens
✓ Schattenlesen (Shadowing) und Nachsprechen
✓ Wortschatzaufbau und Festigung grammatischer Strukturen
✓ Gewöhnung an akademische Hörtexte

🗣 Sprecher: Standarddeutscher Sprecher mit neutraler, klarer Aussprache  
🎧 Inhalt: Vorlesen eines sachlichen deutschen Textes in prüfungsnahem Stil

Tipps zum Lernen:
1. Zuerst ohne Untertitel hören
2. Danach mit deutschen Untertiteln (automatisch erzeugt) erneut anhören
3. Den Text laut nachsprechen (Shadowing)
4. Mehrmals wiederholen – Sprache lernt man durch Wiederholung

💡 Lerntipp:  
Dieses Video lässt sich sehr gut zusammen mit dem Browser‑Add‑on **Language Reactor** verwenden (https://www.languagereactor.com/).  
Damit kannst du Untertitel bequemer steuern, Vokabeln speichern und schwierige Stellen mehrfach im Kontext wiederholen.

Wenn du weitere deutsche Hörübungen möchtest, freue ich mich über einen Kommentar oder ein Abo!

#Deutschlernen #GermanListening #TestDaF #DSH #TELC #Goethe #GermanAudio #DeutschfürAusländer #GermanPractice #GermanReading #Deutschverstehen""",
    # 德福 / 高階考試：聽力重點
    "testdaf_listening": """#TestDaF #Deutschlernen #Hörverstehen #GermanListening
📌 TestDaF / Hochschulprüfung – Hörverstehen-Training mit authentischem Übungstext

In diesem Video hörst du einen deutschen Übungstext im prüfungsnahen Stil. Ideal für:
✓ Vorbereitung auf TestDaF, DSH, telc Hochschule
✓ Training des globalen und selektiven Hörverstehens
✓ Gewöhnung an akademische Hörtexte und typische Prüfungssituationen

🗣 Sprecher: neutrale, deutliche Aussprache in Standarddeutsch  
🎧 Fokus: Hörverstehen, Notizen machen, Struktur erkennen

Lerntipps:
1. Zuerst einmal ohne Untertitel hören und nur grob mitschreiben
2. Beim zweiten Hören gezielt auf Details achten (Zahlen, Argumente, Beispiele)
3. Schwierige Stellen mehrfach wiederholen, bis die Struktur klar ist
4. Zum Schluss laut mitsprechen (Shadowing), um Aussprache und Rhythmus zu üben

💡 Bonus:  
Zusammen mit **Language Reactor** im Browser kannst du Untertitel, Pausen und Wiederholungen noch besser steuern.

Wenn dir dieses Hörtraining hilft, lass gerne einen Kommentar oder ein Abo da.

#TestDaF #DSH #telcC1 #GermanExam #Hörverstehen #DeutschfürStudium""",
    # 德福 / 口語題型
    "testdaf_speaking": """#TestDaF #Deutschlernen #Sprechen #GermanSpeaking
📌 TestDaF Mündliche Prüfung – Sprechanlass / Antwortbausteine zum Mitsprechen

Dieses Video ist für die Vorbereitung auf die mündliche Prüfung gedacht. Ideal für:
✓ TestDaF-Aufgaben zur Beschreibung, Meinungsäußerung und Diskussion
✓ Strukturierte Antwortbausteine (Einleitung – Argumente – Schluss)
✓ Lautes Mitsprechen (Shadowing) für mehr Sicherheit im Ausdruck

🗣 Fokus: flüssiges, zusammenhängendes Sprechen in Prüfungssituationen  
🎯 Ziel: typische Redemittel automatisieren, damit im Ernstfall mehr Kapazität fürs Denken bleibt

💡 Lerntipps:
1. Höre den Text zuerst komplett durch und achte auf Aufbau und Redemittel
2. Spule zurück und sprich einzelne Sätze oder Abschnitte laut nach
3. Pausiere das Video und versuche, ähnliche Antworten mit eigenen Inhalten zu formulieren
4. Wiederhole das Ganze mehrmals an verschiedenen Tagen, damit die Strukturen im Kopf bleiben

 
Dieses Video lässt sich sehr gut zusammen mit dem Browser‑Add‑on **Language Reactor** verwenden (https://www.languagereactor.com/).  
Damit kannst du Untertitel bequemer steuern, Vokabeln speichern und schwierige Stellen mehrfach im Kontext wiederholen.

Wenn du dir mehr Vorlagen für mündliche Prüfungen wünschst, schreib es gern in die Kommentare.

#TestDaF #MündlichePrüfung #DeutschSprechen #Redemittel #GermanOralExam""",
    # 德福 / 書寫題型
    "testdaf_writing": """#TestDaF #Deutschlernen #Schreiben #GermanWriting
📌 TestDaF Schriftlicher Ausdruck – Mustertext / Formulierungshilfen

In diesem Video wird ein Mustertext für die schriftliche Prüfung vorgelesen. Ideal für:
✓ Vorbereitung auf den schriftlichen Ausdruck im TestDaF
✓ Einüben von typischen Einleitungen, Überleitungen und Schlussformulierungen
✓ Wiederkehrende Formulierungen für Argumentation, Beschreibung und Stellungnahme

🗣 Sprecher: ruhige, deutliche Aussprache in Standarddeutsch  
📄 Inhalt: prüfungsnaher Beispieltext, der sich gut als Vorlage oder Inspiration eignet

💡 Lerntipps:
1. Höre den Text einmal komplett, nur um Struktur und Aufbau zu verstehen
2. Lies (oder höre) Abschnitt für Abschnitt und markiere dir nützliche Redemittel
3. Versuche dann, mit denselben Bausteinen eigene Texte zu einem anderen Thema zu formulieren
4. Nutze den Text zum laut Vorlesen, um Schriftbild und Aussprache gleichzeitig zu trainieren

💡 Bonus:  
Dieses Video lässt sich sehr gut zusammen mit dem Browser‑Add‑on **Language Reactor** verwenden (https://www.languagereactor.com/).  
Damit kannst du Untertitel bequemer steuern, Vokabeln speichern und schwierige Stellen mehrfach im Kontext wiederholen.

Wenn du mehr Beispieltexte für schriftliche Prüfungen brauchst, lass gern einen Kommentar oder ein Abo da.

#TestDaF #SchriftlicherAusdruck #DeutschSchreiben #GermanWriting #DeutschPrüfung"""
}

DEFAULT_YT_TEMPLATE_KEY = "general_listening"

def get_speech_config() -> speechsdk.SpeechConfig:
    # 優先從 Streamlit secrets 讀取
    key = st.secrets.get("SPEECH_KEY")
    region = st.secrets.get("SPEECH_REGION")

    if not key or not region:
        st.error(
            "找不到 Azure TTS 金鑰設定。\n"
            "請在 .streamlit/secrets.toml 中設定 SPEECH_KEY 和 SPEECH_REGION。"
        )
        st.stop()

    speech_config = speechsdk.SpeechConfig(
        subscription=key,
        region=region,
    )
    # 預設德語女聲，可在 UI 中覆蓋
    speech_config.speech_synthesis_voice_name = "de-DE-KatjaNeural"
    # 直接輸出 MP3
    speech_config.set_speech_synthesis_output_format(
        speechsdk.SpeechSynthesisOutputFormat.Audio16Khz32KBitRateMonoMp3
    )
    return speech_config


def main():
    st.set_page_config(page_title="Azure TTS Demo", layout="wide")

    st.title("Azure Text-to-Speech 語音合成 Demo")

    # ====== 側邊欄：說明與所有配置 ======
    selected_description_template_key = DEFAULT_YT_TEMPLATE_KEY
    current_description_template = YOUTUBE_DESCRIPTION_TEMPLATES[DEFAULT_YT_TEMPLATE_KEY]
    with st.sidebar:
        st.header("設定與說明")
        with st.expander("使用說明（點我展開 / 收合）", expanded=False):
            st.markdown(
                """
                使用 Azure Speech Service 將文字轉成語音檔案。

                在執行本程式前，請先：
                - 安裝套件：`pip install azure-cognitiveservices-speech streamlit`
                - 設定 Streamlit secrets（推薦）或環境變數：
                  - `SPEECH_KEY`：Azure Speech 資源金鑰（TTS 用）
                  - `SPEECH_REGION`：Azure Speech 資源 region（例如：`eastasia`）
                """
            )
        # st.markdown("---")
        st.subheader("YouTube 說明欄模板")
        yt_template_labels = {
            "一般：聽力 / 閱讀 / 跟讀": "general_listening",
            "德福 Hörverstehen（聽力題）": "testdaf_listening",
            "德福 Mündliche Prüfung（口語題）": "testdaf_speaking",
            "德福 Schriftlicher Ausdruck（寫作題）": "testdaf_writing",
        }
        selected_yt_label = st.selectbox(
            "選擇說明欄用途（會影響模板內容）：",
            list(yt_template_labels.keys()),
            index=0,
        )
        selected_description_template_key = yt_template_labels[selected_yt_label]
        current_description_template = YOUTUBE_DESCRIPTION_TEMPLATES.get(
            selected_description_template_key,
            YOUTUBE_DESCRIPTION_TEMPLATES[DEFAULT_YT_TEMPLATE_KEY],
        )

        with st.expander("查看目前選擇的說明欄模板（可複製調整）", expanded=False):
            st.text_area(
                "目前選擇的 YouTube 說明欄模板（可複製自行調整）：",
                value=current_description_template,
                height=260,
            )

    st.subheader("文本輸入")
    raw_markdown = st.text_area(
        "請貼入 Markdown 文本（會自動去除標記後再送去朗讀）：",
        height=260,
    )

    def clean_markdown(text: str) -> str:
        """簡單清掉常見 Markdown 標記，保留純文字，並盡量保留原始換行。
        特別處理：
        - 保留第一個標題的內容（當成正文開頭），其他標題仍刪除。
        - 去掉常見粗體標記、項目符號與 emoji bullet。
        - 原文中的換行會盡量被保留為行分隔符。
        """
        lines = text.splitlines()
        kept = []
        first_heading_kept = False
        for line in lines:
            stripped = line.strip()
            # 空行：保留為段落分隔（之後會變成一個空行）
            if not stripped:
                kept.append("")
                continue
            # 評分提示這類行直接丟掉
            if stripped.startswith("✅"):
                continue
            # 標題處理
            if stripped.startswith("#"):
                # 只保留第一個標題的文字內容，其餘標題直接略過
                if not first_heading_kept:
                    heading_text = stripped.lstrip("#").strip()
                    if heading_text:
                        # 若標題末尾沒有句號等，補上一個句號，方便之後切句
                        if not heading_text.endswith((".", "!", "?", "。", "！", "？")):
                            heading_text += "."
                        kept.append(heading_text)
                    first_heading_kept = True
                continue
            # 分隔線 / 程式區塊標記
            if stripped.startswith("---") or stripped.startswith("***"):
                continue
            if stripped.startswith("```"):
                continue
            # 去掉常見項目符號與 emoji bullet
            stripped = re.sub(r"^[-*+•✅▶️✔️]\s*", "", stripped)
            # 去掉粗體 / 斜體標記 **text** / *text*
            stripped = re.sub(r"\*\*(.*?)\*\*", r"\1", stripped)
            stripped = re.sub(r"\*(.*?)\*", r"\1", stripped)
            kept.append(stripped)

        # 以換行重新接回文字，以保留原本的行結構
        joined = "\n".join(kept)
        # 壓縮多餘的連續空白行（最多保留兩個換行）
        joined = re.sub(r"\n{3,}", "\n\n", joined)
        return joined

    def split_sentences(text: str):
        """改為只依原始換行切成「行」，不再用標點符號斷句。

        原則：
        - 每一行視為一個朗讀單位。
        - 原本為空行的，保留為空字串，最後在顯示時仍是一個換行。
        - 這樣可避免像「z.b.」這類包含句點的縮寫被誤切斷。
        """
        sentences = []
        for line in text.splitlines():
            # 直接保留原行（含空行），只做右側去除換行符號
            sentences.append(line.rstrip("\n"))
        return sentences

    cleaned_text = clean_markdown(raw_markdown) if raw_markdown.strip() else ""

    display_text = ""
    sentences = []
    if cleaned_text:
        sentences = split_sentences(cleaned_text)
        display_text = "\n".join(sentences)

    # ====== 長文本提示與分段設定（自動依句數切割） ======
    segmentation_mode = "single"  # "single" 或 "auto"
    sentences_per_segment = 5
    word_count = 0

    if cleaned_text:
        word_count = len(cleaned_text.split())

    if sentences:
        st.info(
            f"目前清洗後文本約 {word_count} 個詞，共 {len(sentences)} 句。\n"
            "Azure 單次合成約 10 分鐘上限，建議使用自動分段以避免超時或被取消。"
        )
        seg_choice = st.radio(
            "長文本處理方式：",
            ["整篇一次合成", "自動分段（建議）"],
            index=1,
        )
        if seg_choice == "自動分段（建議）":
            segmentation_mode = "auto"
            sentences_per_segment = st.slider(
                "每段大約幾句？（較小較安全）",
                min_value=3,
                max_value=12,
                value=5,
                step=1,
                help="程式會依序每 N 句切一段，最後一段可能略短。句數愈少，單段長度愈安全。",
            )
            approx_segments = max(1, (len(sentences) + sentences_per_segment - 1) // sentences_per_segment)
            st.caption(
                f"目前預估會切成約 {approx_segments} 段（實際依句數微調）。"
            )

    combined_for_description = ""
    if display_text:
        st.text_area(
            "預處理後（每句一行）將送給 Azure 朗讀的純文字（可檢查用）：",
            value=display_text,
            height=220,
        )

    # ====== 側邊欄：語音 / 輸出設定與用量提示 ======
    with st.sidebar:
        st.markdown("---")
        start_clicked = st.button("開始語音合成")
        st.markdown("---")
        st.subheader("語音與輸出設定")

        # 一些常用的 Azure Neural voice 範例
        voice_options = {
            "德語 女聲（de-DE-KatjaNeural）": "de-DE-KatjaNeural",
            "德語 男聲（de-DE-ConradNeural）": "de-DE-ConradNeural",
            "英文 女聲（en-US-JennyNeural）": "en-US-JennyNeural",
            "英文 男聲（en-US-GuyNeural）": "en-US-GuyNeural",
            "自訂 voice 名稱…": "custom",
        }

        selected_voice_label = st.selectbox(
            "選擇一個 Azure 語音（voice）：",
            list(voice_options.keys()),
            index=0,
        )

        custom_voice = ""
        if voice_options[selected_voice_label] == "custom":
            custom_voice = st.text_input(
                "請輸入自訂的 Azure 語音名稱（例如 de-DE-ElkeNeural）：",
                value="",
            )

        # 最終要拿來送給 Azure 的 voice 名稱
        voice = custom_voice if custom_voice.strip() else voice_options[selected_voice_label]

        mode = st.radio(
            "輸出類型：",
            ["只產生 MP3 音檔", "產生黑底 MP4 影片"],
            index=1,  # 預設改為「產生黑底 MP4 影片」
        )

        video_lead_seconds = st.slider(
            "影片開頭空白秒數（僅影響 MP4，MP3 不延遲）：",
            min_value=0,
            max_value=10,
            value=5,
            step=1,
        )

        auto_play = st.checkbox(
            "合成完成後在網頁中立即朗讀（自動播放，可暫停/繼續）",
            value=True,
        )

        base_name = st.text_input(
            "自訂檔名前綴（選填，不填時會用 Markdown 第一個標題 + 時間戳）：",
            value="",
        )

        st.markdown("---")
        add_description = False
        if display_text:
            st.caption(f"目前將使用：「{selected_yt_label}」這個說明欄模板")
            add_description = st.checkbox(
                "產生包含固定模板的 YouTube 說明欄文本",
                value=False,
            )

        st.markdown("---")
        with st.expander("文字用量（點我展開 / 收合）", expanded=False):
            char_count = len(cleaned_text)
            monthly_free_chars = 500_000  # F0 / Free Tier 每月約 0.5M 字元
            if char_count > 0:
                ratio = char_count / monthly_free_chars * 100
                st.info(
                    f"本次送給 Azure 的文字約 {char_count} 個字元。\n"
                    f"若以每月免費 {monthly_free_chars:,} 字元計算，約占理論免費額度的 {ratio:.2f}%。"
                )
            else:
                st.write("目前還沒有可送給 Azure 的文字。")

    # 產生 YouTube 說明欄文本（顯示在主區）
    if display_text and 'add_description' in locals() and add_description:
        template_body = YOUTUBE_DESCRIPTION_TEMPLATES.get(
            selected_description_template_key,
            YOUTUBE_DESCRIPTION_TEMPLATES[DEFAULT_YT_TEMPLATE_KEY],
        )
        combined_for_description = f"{display_text}\n\n\n{template_body}"
        st.text_area(
            "YouTube 說明欄（已包含本次文本與固定說明，可直接複製）：",
            value=combined_for_description,
            height=260,
        )

    if start_clicked:
        if not cleaned_text.strip():
            st.error("請先輸入要轉成語音的 Markdown 文本。")
            return

        # 根據 Markdown 第一個標題 + 時間戳產生檔名基底
        heading_match = re.search(r"^\s*#+\s+(.*)$", raw_markdown, flags=re.MULTILINE)
        heading = heading_match.group(1).strip() if heading_match else "output"

        # 使用者如有自訂前綴，優先使用
        base_label = base_name.strip() if base_name.strip() else heading

        # 簡單清理檔名：移除不適合的符號
        def sanitize_filename(s: str) -> str:
            s = s.strip()
            # 只保留常見安全字元，其餘用底線代替
            return "".join(
                (c if c.isalnum() or c in " _-一二三四五六七八九零〇壹貳參肆伍陸柒捌玖拾百千萬億" else "_")
                for c in s
            ).replace(" ", "_")

        safe_label = sanitize_filename(base_label) or "output"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        final_base = f"{safe_label}_{timestamp}"

        # 輸出資料夾
        output_dir = "azure_outputs"
        os.makedirs(output_dir, exist_ok=True)

        audio_filename = os.path.join(output_dir, f"{final_base}.mp3")
        video_filename = os.path.join(output_dir, f"{final_base}.mp4")
        subtitle_txt_filename = os.path.join(output_dir, f"{final_base}.txt")

        # 將清洗後、每句一行的文本輸出成 .txt，方便餵給 YouTube 做字幕
        if display_text:
            try:
                with open(subtitle_txt_filename, "w", encoding="utf-8") as f:
                    f.write(display_text)
            except Exception as e:
                st.warning(f"輸出字幕用文本檔時發生錯誤：{e}")

        # 準備 Azure TTS
        speech_config = get_speech_config()
        if voice:
            speech_config.speech_synthesis_voice_name = voice

        # 準備要送進 TTS 的分段文本
        def build_segments_auto(all_sentences, per_segment: int):
            if not all_sentences:
                return []
            if per_segment <= 0:
                return [" ".join(all_sentences).strip()]
            segments = []
            total = len(all_sentences)
            start = 0
            while start < total:
                end = min(start + per_segment, total)
                segments.append(" ".join(all_sentences[start:end]).strip())
                start = end
            return [s for s in segments if s]

        # 依長文本模式決定分段；否則整篇一次送出
        tts_segments = []
        if segmentation_mode == "auto" and sentences:
            tts_segments = build_segments_auto(sentences, sentences_per_segment)
        else:
            # 退而求其次，以 cleaned_text 當作單一段
            tts_segments = [cleaned_text]

        if not tts_segments:
            st.error("沒有可用來語音合成的文本分段。")
            return

        st.info(f"本次將分成 {len(tts_segments)} 段進行語音合成。")

        # 逐段合成，輸出多個臨時音檔，再之後合併
        part_files = []
        progress_bar = st.progress(0)

        for idx, segment in enumerate(tts_segments, start=1):
            part_path = os.path.join(output_dir, f"{final_base}_part_{idx:03d}.mp3")
            audio_config_part = speechsdk.audio.AudioConfig(filename=part_path)
            synthesizer_part = speechsdk.SpeechSynthesizer(
                speech_config=speech_config,
                audio_config=audio_config_part,
            )

            with st.spinner(f"Azure 正在合成第 {idx}/{len(tts_segments)} 段…"):
                result = synthesizer_part.speak_text_async(segment).get()

            if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                part_files.append(part_path)
                progress_bar.progress(idx / len(tts_segments))
            elif result.reason == speechsdk.ResultReason.Canceled:
                cancellation = result.cancellation_details
                st.error(
                    f"第 {idx} 段合成被取消：{cancellation.reason} - {cancellation.error_details}"
                )
                return
            else:
                st.error(f"第 {idx} 段合成結果未知：{result.reason}")
                return

        progress_bar.progress(1.0)

        # 所有分段皆成功合成後，使用 ffmpeg concat 模式合併為一個完整 MP3
        concat_list_path = os.path.join(output_dir, f"{final_base}_concat_list.txt")
        try:
            with open(concat_list_path, "w", encoding="utf-8") as f:
                for part in part_files:
                    # ffmpeg concat 檔案列表格式：file 'path'
                    f.write(f"file '{os.path.abspath(part)}'\n")

            with st.spinner("正在合併各段音檔為完整 MP3…"):
                subprocess.run(
                    [
                        "ffmpeg",
                        "-y",
                        "-f",
                        "concat",
                        "-safe",
                        "0",
                        "-i",
                        concat_list_path,
                        "-c",
                        "copy",
                        audio_filename,
                    ],
                    stdin=subprocess.DEVNULL,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    check=True,
                )
            # 合併成功後，清理中間切片檔與清單檔，只保留完整 MP3
            for part in part_files:
                try:
                    os.remove(part)
                except Exception:
                    pass
            try:
                os.remove(concat_list_path)
            except Exception:
                pass
        except subprocess.CalledProcessError as e:
            st.error(f"合併分段音檔時 ffmpeg 發生錯誤：{e}")
            return
        except Exception as e:
            st.error(f"合併分段音檔時發生錯誤：{e}")
            return

        st.success(
            f"語音合成完成，已輸出音檔：{audio_filename}\n"
            f"字幕用純文字檔：{subtitle_txt_filename}"
        )

        # 播放 MP3（只顯示一個播放器；若勾選自動播放則用 HTML5 autoplay，否則用 st.audio）
        try:
            with open(audio_filename, "rb") as f:
                audio_bytes = f.read()

            if auto_play:
                b64_audio = base64.b64encode(audio_bytes).decode("utf-8")
                components.html(
                    f"""
                    <audio controls autoplay>
                        <source src="data:audio/mpeg;base64,{b64_audio}" type="audio/mpeg">
                        Your browser does not support the audio element.
                    </audio>
                    """,
                    height=80,
                )
            else:
                st.audio(audio_bytes, format="audio/mp3")
        except Exception as e:
            st.warning(f"音檔已產生，但讀取播放時發生錯誤：{e}")

        # 若選擇產生影片，呼叫 ffmpeg 做黑底影片（使用合併後的完整音檔）
        if mode == "產生黑底 MP4 影片":
            video_progress = st.progress(0)
            with st.spinner("正在用 ffmpeg 生成黑底影片…"):
                try:
                    # 將音訊延遲指定秒數，使影片開頭先有幾秒無聲畫面
                    delay_ms = int(locals().get("video_lead_seconds", 5) * 1000)
                    subprocess.run(
                        [
                            "ffmpeg",
                            "-y",
                            "-f",
                            "lavfi",
                            "-i",
                            "color=c=black:s=1920x1080:r=30",
                            "-i",
                            audio_filename,
                            "-af",
                            f"adelay={delay_ms}|{delay_ms}",
                            "-shortest",
                            video_filename,
                        ],
                        stdin=subprocess.DEVNULL,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        check=True,
                    )
                    video_progress.progress(100)
                    st.success(f"影片生成完成：{video_filename}")
                    st.video(video_filename)
                except subprocess.CalledProcessError as e:
                    st.error(f"生成影片時 ffmpeg 發生錯誤：{e}")


if __name__ == "__main__":
    main()
