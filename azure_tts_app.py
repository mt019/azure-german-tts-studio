import os
import subprocess
import re
from datetime import datetime

import streamlit as st
import azure.cognitiveservices.speech as speechsdk
import streamlit.components.v1 as components
import base64


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

    # YouTube 說明欄預設內容（優化版）
    youtube_description = """#Deutschlernen #GermanListening #TELC #Deutschverstehen
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

#Deutschlernen #GermanListening #TestDaF #DSH #TELC #Goethe #GermanAudio #DeutschfürAusländer #GermanPractice #GermanReading #Deutschverstehen"""

    # ====== 側邊欄：說明與所有配置 ======
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

    st.subheader("文本輸入")
    raw_markdown = st.text_area(
        "請貼入 Markdown 文本（會自動去除標記後再送去朗讀）：",
        height=260,
    )

    def clean_markdown(text: str) -> str:
        """簡單清掉常見 Markdown 標記，保留純文字。"""
        lines = text.splitlines()
        kept = []
        for line in lines:
            stripped = line.strip()
            # 去除標題/分隔線/程式區塊標記等
            if not stripped:
                continue
            if stripped.startswith("#"):
                continue
            if stripped.startswith("---") or stripped.startswith("***"):
                continue
            if stripped.startswith("```"):
                continue
            # 去掉項目符號開頭
            if stripped[0] in "-*+" and (len(stripped) == 1 or stripped[1] == " "):
                stripped = stripped[1:].lstrip()
            kept.append(stripped)
        joined = " ".join(kept)
        return " ".join(joined.split())

    def split_sentences(text: str):
        """簡單依 . ? ! 切成句子。"""
        parts = re.split(r"(?<=[\.?!])\s+", text)
        return [p.strip() for p in parts if p.strip()]

    cleaned_text = clean_markdown(raw_markdown) if raw_markdown.strip() else ""

    display_text = ""
    if cleaned_text:
        sentences = split_sentences(cleaned_text)
        display_text = "\n".join(sentences)

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
        combined_for_description = f"{display_text}\n\n\n{youtube_description}"
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

        audio_config = speechsdk.audio.AudioConfig(filename=audio_filename)
        synthesizer = speechsdk.SpeechSynthesizer(
            speech_config=speech_config,
            audio_config=audio_config,
        )

        with st.spinner("Azure 正在合成語音，請稍候…"):
            result = synthesizer.speak_text_async(cleaned_text).get()

        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
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

            # 若選擇產生影片，呼叫 ffmpeg 做黑底影片
            if mode == "產生黑底 MP4 影片":
                with st.spinner("正在用 ffmpeg 生成黑底影片…"):
                    try:
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
                                "-shortest",
                                video_filename,
                            ],
                            check=True,
                        )
                        st.success(f"影片生成完成：{video_filename}")
                        st.video(video_filename)
                    except subprocess.CalledProcessError as e:
                        st.error(f"生成影片時 ffmpeg 發生錯誤：{e}")
        elif result.reason == speechsdk.ResultReason.Canceled:
            cancellation = result.cancellation_details
            st.error(f"合成被取消：{cancellation.reason} - {cancellation.error_details}")
        else:
            st.error(f"未知結果：{result.reason}")


if __name__ == "__main__":
    main()
