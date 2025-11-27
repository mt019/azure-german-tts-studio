from TTS.api import TTS
import wave
import contextlib
from tqdm import tqdm
import time

def count_audio_length(path):
    with contextlib.closing(wave.open(path,'r')) as f:
        frames = f.getnframes()
        rate = f.getframerate()
        return frames / float(rate)

def fmt(t):
    hrs = int(t//3600)
    mins = int((t%3600)//60)
    secs = int(t%60)
    millis = int((t-int(t))*1000)
    return f"{hrs:02d}:{mins:02d}:{secs:02d},{millis:03d}"

print("加载 Thorsten Tacotron2-DDC（老男人+快速生成）...")
model = TTS("tts_models/de/thorsten/tacotron2-DDC").to("cpu")
print("模型加载完成！")

# 载入文本并处理空行
with open("text.txt", "r", encoding="utf-8") as f:
    lines = [l.strip() for l in f.readlines() if l.strip()]

full_text = " ".join(lines)

print("\n生成语音中...")

# 视觉进度条
for i in tqdm(range(100), desc="语音合成中", unit="%"):
    time.sleep(0.01)

start_time = time.time()

model.tts_to_file(
    text=full_text,
    file_path="output.wav"
)

print(f"\n语音生成完成！耗时 {time.time()-start_time:.2f} 秒")

# 计算音频时长
duration = count_audio_length("output.wav")
avg = duration / len(lines)

print("开始生成字幕 SRT...")

# 字幕进度条
for i in tqdm(range(len(lines)), desc="字幕生成中", unit="行"):
    time.sleep(0.002)

with open("output.srt", "w", encoding="utf-8") as f:
    for i, line in enumerate(lines):
        start = i * avg
        end = start + avg
        f.write(f"{i+1}\n")
        f.write(f"{fmt(start)} --> {fmt(end)}\n")
        f.write(line + "\n\n")

print("\n全部完成！")
print("输出文件：output.wav  +  output.srt")