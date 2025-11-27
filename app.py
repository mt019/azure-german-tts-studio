import streamlit as st
import re
from num2words import num2words
from TTS.api import TTS
import subprocess
import time

# =============== 文本处理函数 =====================

def clean_markdown(text: str) -> str:
    lines = text.splitlines()
    kept = []
    for line in lines:
        if line.strip().startswith("#"):
            continue
        kept.append(line)
    joined = " ".join(kept)
    joined = re.sub(r"\s+", " ", joined).strip()
    return joined

def split_sentences(text: str):
    rough = re.split(r"(?<=[\.\?\!])\s+", text)
    units = []
    for s in rough:
        if not s.strip():
            continue
        clauses = [c.strip() for c in s.split(",") if c.strip()]
        units.extend(clauses)
    return units

def num_de(n: int) -> str:
    return num2words(n, lang="de")

def convert_numbers_for_tts(sentence: str) -> str:
    s = sentence

    s = re.sub(
        r"(\d{4})\s*[–-]\s*(\d{4})",
        lambda m: f"{num_de(int(m.group(1)))} bis {num_de(int(m.group(2)))}",
        s,
    )

    s = re.sub(
        r"(\d{1,2})\s*[–-]\s*(\d{1,2})-Jährigen",
        lambda m: f"{num_de(int(m.group(1)))} bis {num_de(int(m.group(2)))} Jährigen",
        s,
    )

    s = re.sub(
        r"(\d+)\s*%",
        lambda m: f"{num_de(int(m.group(1)))} Prozent",
        s,
    )

    s = re.sub(
        r"(\d{1,2})\s*[–-]\s*(\d{1,2})",
        lambda m: f"{num_de(int(m.group(1)))} bis {num_de(int(m.group(2)))}",
        s,
    )

    s = re.sub(
        r"\b(\d{4})\b",
        lambda m: num_de(int(m.group(1))),
        s,
    )

    s = re.sub(
        r"\b(\d+)\b",
        lambda m: num_de(int(m.group(1))),
        s,
    )

    s = s.replace("%", " Prozent")
    s = re.sub(r"[()]+", " ", s)
    s = s.replace("–", " ").replace("-", " ")
    s = re.sub(r"\s+", " ", s).strip()

    return s



# ====================== UI ==========================

st.set_page_config(page_title="德語語音生成工具", layout="wide")

st.title("德語語音 + YouTube字幕生成工具")

# ================= YouTube 說明欄文本 ================
youtube_description = """#Deutschlernen #GermanListening #TestDaF
📌 Deutsche Sprachübung – Vorlesen eines deutschen Textes für Prüfungsvorbereitung

In diesem Video wird ein deutscher Übungstext langsam und deutlich vorgelesen. Ideal für:
✓ Vorbereitung auf TestDaF / DSH / Goethe / TELC
✓ Verbesserung der Hörverstehenskompetenz
✓ Schattenlesen (Shadowing)
✓ Wortschatz- und Strukturerwerb
✓ Training des akademischen Hörens

🗣 Sprecher: Standarddeutscher männlicher Sprecher (neutrale, klare Aussprache)
🎧 Inhalt: Vorlesen eines sachlichen deutschen Textes mit naturlangem Sprechtempo

Tipp zum Lernen:
1. Erst ohne Untertitel hören
2. Dann mit deutschen Untertiteln (automatisch erkannt)
3. Danach den Text laut nachsprechen
4. Wiederholung – Sprache entsteht durch Wiederholung

Wenn du weitere deutsche Hörübungen möchtest, hinterlasse gerne einen Kommentar!

#Deutschlernen #GermanListening #TestDaF #DSH #TELC #Goethe #GermanAudio #DeutschfürAusländer #GermanPractice #GermanReading #Deutschverstehen"""

input_mode = st.radio(
    "請選擇輸入模式",
    ["我有自然朗讀文本 + Markdown原文", "我只有Markdown原文"],
)


markdown_text = st.text_area(
    "請貼入Markdown原文：",
    height=300
)

tts_text = None

if input_mode == "我有自然朗讀文本 + Markdown原文":
    tts_text = st.text_area(
        "請貼入自然朗讀文本（無Markdown、無符號、純口語）：",
        height=250
    )


generate_video = st.checkbox("生成 MP4 影片（黑底 + 音訊）")
start_button = st.button("開始生成")

# ===================== 開始流程 ======================

if start_button:

    if not markdown_text.strip():
        st.error("錯誤：你沒有輸入Markdown文本")
        st.stop()

    st.write("正在處理文本…")

    # 第一种模式：你已有自然朗讀版本
    if input_mode == "我有自然朗讀文本 + Markdown原文":

        if not tts_text.strip():
            st.error("錯誤：你沒有輸入自然朗讀文本")
            st.stop()

        clean_md = clean_markdown(markdown_text)
        youtube_lines = split_sentences(clean_md)

        with open("text_youtube.txt", "w", encoding="utf-8") as f:
            for line in youtube_lines:
                f.write(line + "\n")

        with open("text_tts.txt", "w", encoding="utf-8") as f:
            f.write(tts_text)

        final_tts = tts_text

        st.success("已使用你自己的自然朗讀文本")

    # 第二种模式：你只有Markdown原文
    else:
        st.write("→ 自動處理 Markdown...")

        clean_md = clean_markdown(markdown_text)
        units = split_sentences(clean_md)

        # YouTube 用字幕
        with open("text_youtube.txt", "w", encoding="utf-8") as f:
            for u in units:
                f.write(u + "\n")

        st.write("→ 自動生成自然朗讀版本...")

        tts_lines = []
        progress = st.progress(0)
        for i, u in enumerate(units):
            tts_lines.append(convert_numbers_for_tts(u))
            progress.progress((i+1)/len(units))

        final_tts = " ".join(tts_lines)

        with open("text_tts.txt", "w", encoding="utf-8") as f:
            for u in tts_lines:
                f.write(u + "\n")

        st.success("已自動生成自然朗讀文本")


    # 推理
    st.write("正在載入語音模型…")
    model = TTS("tts_models/de/thorsten/vits").to("cpu")

    st.write("正在合成語音 output.wav …")
    time.sleep(1)
    model.tts_to_file(full_tts_text:=final_tts, file_path="output.wav")
    st.success("output.wav 已生成")

    # 视频
    if generate_video:
        st.write("正在生成影片 output.mp4 …")
        subprocess.run([
            "ffmpeg", "-y",
            "-f", "lavfi", "-i", "color=c=black:s=1920x1080:r=30",
            "-i", "output.wav",
            "-shortest", "output.mp4"
        ])
        st.success("output.mp4 已生成")

    st.subheader("=== text_tts.txt ===")
    st.text(final_tts)

    st.subheader("=== text_youtube.txt ===")
    clean_view = open("text_youtube.txt",encoding="utf-8").read()
    st.text(clean_view)

    st.write("YouTube 說明欄文本（不顯示全文）")

    import streamlit.components.v1 as components

    components.html(f'''
    <button onclick="navigator.clipboard.writeText(`{youtube_description}`)"
    style="padding:10px 20px;font-size:16px;">
    📋 Copy Description
    </button>
    ''')

    # 保留 YouTube 說明文本副本至本地
    with open("youtube_description.txt", "w", encoding="utf-8") as f:
        f.write(youtube_description)

    st.success("全部完成！")