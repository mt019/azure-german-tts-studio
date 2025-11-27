from TTS.api import TTS
import re
import wave
import contextlib
import time
import torch

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

def split_text_smart(text):
    text = re.sub(r'\s+', ' ', text)
    return re.split(r'(?<=[\.\?\!])\s', text)

print("正在检测 GPU / MPS 支持...")

if torch.backends.mps.is_available():
    device="mps"
    print("检测到 MPS GPU 支持，将使用 Apple GPU 加速")
elif torch.cuda.is_available():
    device="cuda"
    print("检测到 CUDA GPU 支持，将使用 NVIDIA 加速")
else:
    device="cpu"
    print("没有可用 GPU，将使用 CPU")

print("\n正在加载 Thorsten 德语标准发音模型...")
model = TTS("tts_models/de/thorsten/vits").to(device)
print("模型加载完成！")

with open("text.txt", "r", encoding="utf-8") as f:
    raw = f.read()

print("\n正在进行朗读优化预处理...")

sentences = split_text_smart(raw)

processed = []
for s in sentences:
    s = s.replace("%"," Prozent")
    s = s.replace("1991","neunzehnhunderteinundneunzig")
    s = s.replace("2002","zweitausendundzwei")
    s = s.replace("2003","zweitausendunddrei")
    processed.append(s)

full_text = " ".join(processed)

print("\n开始生成语音...")
start_time = time.time()

model.tts_to_file(
    text=full_text,
    file_path="output.wav"
)

print(f"语音生成完成！耗时 {time.time()-start_time:.2f} 秒")

duration = count_audio_length("output.wav")

avg = duration / len(sentences)

print("开始生成字幕 SRT...")

with open("output.srt", "w", encoding="utf-8") as f:
    for i, line in enumerate(sentences):
        start = i * avg
        end = start + avg
        f.write(f"{i+1}\n")
        f.write(f"{fmt(start)} --> {fmt(end)}\n")
        f.write(line + "\n\n")

print("\n全部完成！")
print(f"总音频时长：{duration:.2f} 秒")
print(f"句子数：{len(sentences)}")
print("输出文件：")
print(" - output.wav")
print(" - output.srt")