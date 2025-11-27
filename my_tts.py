import subprocess
from TTS.api import TTS
import os

BACKGROUND_COLOR = "black"   # 可选：white / black / gray
VIDEO_OUTPUT = "output.mp4"
AUDIO_OUTPUT = "output.wav"
RESOLUTION = "1920x1080"
FPS = 30

print("加载 Thorsten 德语 TTS 模型...")
model = TTS("tts_models/de/thorsten/vits").to("mps")
print("模型加载完成")

print("载入文本...")
with open("text.txt", "r", encoding="utf-8") as f:
    text = f.read().strip()

print("生成语音文件...")
model.tts_to_file(text=text, file_path=AUDIO_OUTPUT)
print("语音完成")

print("生成视频（无字幕版本）...")
cmd = [
    "ffmpeg",
    "-y",
    "-f", "lavfi",
    "-i", f"color=c={BACKGROUND_COLOR}:s={RESOLUTION}:r={FPS}",
    "-i", AUDIO_OUTPUT,
    "-shortest",
    VIDEO_OUTPUT
]
subprocess.run(cmd)

print("全部完成！！！")
print(f"输出：\n{AUDIO_OUTPUT}\n{VIDEO_OUTPUT}")