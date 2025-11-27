import re
import time
import subprocess
from tqdm import tqdm
from TTS.api import TTS
from num2words import num2words

try:
    import torch
    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False

# ========= 使用者可調整參數 =========
BACKGROUND_COLOR = "black"
RESOLUTION = "1920x1080"
FPS = 30
AUDIO_OUT = "output.wav"
VIDEO_OUT = "output.mp4"
SOURCE_FILE = "text.md"
# ==================================


def clean_markdown(text: str) -> str:
    """移除以 # 開頭的 Markdown 標題，只保留正文。"""
    lines = text.splitlines()
    kept = []
    for line in lines:
        if line.strip().startswith("#"):
            continue
        kept.append(line)
    # 用空白把行接起來，避免奇怪換行
    joined = " ".join(kept)
    # 正規化空白
    joined = re.sub(r"\s+", " ", joined).strip()
    return joined


def split_sentences(text: str):
    """
    粗略以 . ? ! 作為句子切分依據，
    然後再用逗號切成更短的「小句」，方便 YouTube 字幕對齊。
    """
    # 先依標點切成句子
    rough_sentences = re.split(r"(?<=[\.\?\!])\s+", text)
    units = []
    for s in rough_sentences:
        s = s.strip()
        if not s:
            continue
        # 再用逗號切成短子句
        clauses = [c.strip() for c in s.split(",") if c.strip()]
        units.extend(clauses)
    return units


def num_de(n: int) -> str:
    """整數轉德文文字。"""
    return num2words(n, lang="de")


def convert_numbers_for_tts(sentence: str) -> str:
    """
    專給 TTS 用的文本轉換：
    - 數字區間 → 「X bis Y」
    - 年份區間 → 「neunzehnhunderteinundneunzig bis zweitausendundzwei」這種
    - % → 「Prozent」
    - 其他數字 → 全部轉成 num2words 德文拼寫
    - 移除括號等不必要符號
    """

    s = sentence

    # 先處理年分區間，例如 1991–2002 或 1991-2002
    s = re.sub(
        r"(\d{4})\s*[–-]\s*(\d{4})",
        lambda m: f"{num_de(int(m.group(1)))} bis {num_de(int(m.group(2)))}",
        s,
    )

    # 處理「年齡區間 + Jährigen」例如 25–29-Jährigen
    s = re.sub(
        r"(\d{1,2})\s*[–-]\s*(\d{1,2})-Jährigen",
        lambda m: f"{num_de(int(m.group(1)))} bis {num_de(int(m.group(2)))} Jährigen",
        s,
    )

    # 百分比：23 % 或 23%
    s = re.sub(
        r"(\d+)\s*%",
        lambda m: f"{num_de(int(m.group(1)))} Prozent",
        s,
    )

    # 一般數字區間：25–29 / 20-24
    s = re.sub(
        r"(\d{1,2})\s*[–-]\s*(\d{1,2})",
        lambda m: f"{num_de(int(m.group(1)))} bis {num_de(int(m.group(2)))}",
        s,
    )

    # 四位數年份（剩下來的）
    s = re.sub(
        r"\b(\d{4})\b",
        lambda m: num_de(int(m.group(1))),
        s,
    )

    # 其他數字
    s = re.sub(
        r"\b(\d+)\b",
        lambda m: num_de(int(m.group(1))),
        s,
    )

    # 殘留的百分比符號（如果有）一律變成 "Prozent"
    s = s.replace("%", " Prozent")

    # 括號直接拿掉
    s = re.sub(r"[()]+", " ", s)

    # en-dash、一般 dash 變成空白（主要前面已處理區間）
    s = s.replace("–", " ").replace("-", " ")

    # 多餘空白壓縮
    s = re.sub(r"\s+", " ", s).strip()

    return s


def detect_device() -> str:
    """偵測是否有 MPS（Apple GPU），否則用 CPU。"""
    if HAS_TORCH:
        try:
            if torch.backends.mps.is_available():
                return "mps"
        except Exception:
            pass
    return "cpu"


def main():
    print("====================================")
    print("   德語朗讀 + YouTube 字幕自動生成")
    print("====================================")

    # 讀取 Markdown 原文
    print("\n[1/5] 讀取 Markdown 原文...", flush=True)
    with open(SOURCE_FILE, "r", encoding="utf-8") as f:
        raw = f.read()

    # 清理 Markdown 標題
    print("[2/5] 清理 Markdown 標題與多餘空白...", flush=True)
    cleaned = clean_markdown(raw)

    # 切成短句 / 子句
    print("[3/5] 進行句子與子句切分...", flush=True)
    units = split_sentences(cleaned)
    units = [u for u in units if u]

    # 生成 YouTube 用字幕文本（保留數字和符號）
    print("    生成 text_youtube.txt ...", flush=True)
    with open("text_youtube.txt", "w", encoding="utf-8") as f_y:
        for u in units:
            f_y.write(u.strip() + "\n")
    print("    text_youtube.txt 完成 ✓")

    # 生成 TTS 用朗讀文本（轉數字 → 德文）
    print("    生成 text_tts.txt（轉換數字、清理符號）...", flush=True)
    tts_lines = []
    for u in tqdm(units, desc="    處理 TTS 文本", unit="句"):
        tts_lines.append(convert_numbers_for_tts(u))

    full_tts_text = " ".join(tts_lines)

    with open("text_tts.txt", "w", encoding="utf-8") as f_t:
        for line in tts_lines:
            f_t.write(line + "\n")
    print("    text_tts.txt 完成 ✓")

    # 載入 TTS 模型
    print("\n[4/5] 載入 Thorsten 德語 TTS 模型...", flush=True)
    device = detect_device()
    print(f"    使用裝置：{device}", flush=True)
    model = TTS("tts_models/de/thorsten/vits").to(device)
    print("    模型載入完成 ✓")

    # 生成語音
    print("\n    開始生成語音檔 output.wav ...", flush=True)
    for _ in tqdm(range(100), desc="    語音生成進度", unit="%"):
        time.sleep(0.01)

    start = time.time()
    model.tts_to_file(text=full_tts_text, file_path=AUDIO_OUT)
    elapsed = time.time() - start
    print(f"    語音生成完成 ✓ （耗時 {elapsed:.2f} 秒）")

    # 生成影片（純背景 + 音訊）
    print("\n[5/5] 使用 ffmpeg 生成影片 output.mp4 ...", flush=True)
    cmd = [
        "ffmpeg",
        "-y",
        "-f", "lavfi",
        "-i", f"color=c={BACKGROUND_COLOR}:s={RESOLUTION}:r={FPS}",
        "-i", AUDIO_OUT,
        "-shortest",
        VIDEO_OUT,
    ]
    try:
        subprocess.run(cmd, check=True)
        print("    影片生成完成 ✓")
    except Exception as e:
        print("    生成影片時發生錯誤（可能未安裝 ffmpeg）：", e)

    print("\n====================================")
    print("   全部完成！輸出檔案如下：")
    print("   - text_youtube.txt （上傳 YouTube 字幕用，保留數字符號）")
    print("   - text_tts.txt      （老男人朗讀用，數字轉德文文字）")
    print("   - output.wav        （德語朗讀音檔）")
    print("   - output.mp4        （純背景影片，可直接丟 YouTube）")
    print("====================================")


if __name__ == "__main__":
    main()