# German TTS Lab – Azure Speech + Streamlit

## English

I built this small tool to turn German (or other language) text into high‑quality audio and simple black‑screen videos using **Azure Speech Service (Text‑to‑Speech)** and **Streamlit**.

### What this app does for me

- I paste **Markdown text**, and the app automatically strips headings, lists and other markup so only clean, readable text is left.
- It splits the cleaned text into **one sentence per line**, which makes it easy for me to check and reuse the text.
- It uses Azure Neural Voices to synthesize **MP3 audio**.
- I can optionally generate a **black‑screen MP4 video** (handy for quick YouTube uploads).
- After synthesis, I can choose to **auto‑play the audio in the browser** (with pause / resume) or just play it manually.
- Audio and video files are stored in `azure_outputs/` with filenames that include:
  - the first Markdown heading (cleaned)
  - a timestamp (`YYYYMMDD_HHMMSS`)
- I can tick an option to **generate a YouTube description**, combining the current text with a reusable German description template.

---

### Requirements

- Python 3.9+ (recommended)  
- An Azure Speech Service resource (with **Key** and **Region**)

I install the main dependencies with:

```bash
pip install streamlit azure-cognitiveservices-speech
```

---

### Azure keys (Streamlit secrets)

I use `st.secrets` to load my Azure keys.

1. In the project root I create the folder:

   ```bash
   mkdir -p .streamlit
   ```

2. Then I add `.streamlit/secrets.toml` (this file is **not** tracked by git; `.gitignore` already excludes it):

   ```toml
   SPEECH_KEY = "my Azure Speech Key"
   SPEECH_REGION = "my region, e.g. eastasia"
   ```

When I start Streamlit, the app reads `st.secrets["SPEECH_KEY"]` and `st.secrets["SPEECH_REGION"]`.

> If I share this repo, I can add a `.streamlit/secrets.toml.example` as a template, but never commit real keys.

---

### How I run the Azure TTS app

In the project root:

```bash
streamlit run azure_tts_app.py
```

The browser opens automatically (or I go to `http://localhost:8501`).

My workflow in the UI:

1. **Paste Markdown text**
   - The app:
     - removes headings (any line starting with `#`)
     - removes common Markdown markup and bullet symbols
     - joins everything into clean plain text.
2. **Check the “one sentence per line” view**
   - The app splits by `.`, `?`, `!` into sentences and shows them one per line.
   - Under that, it shows how many characters will be sent to Azure and roughly what percentage of the free 500k‑character quota this run consumes.
3. **Voice and output settings**
   - I pick an Azure Neural Voice (a few German/English examples are provided, or I can type a custom voice name).
   - I choose output type:
     - only MP3
     - black‑screen MP4 (using `ffmpeg`)
   - I choose whether to **auto‑play after synthesis**:
     - if enabled, the app uses an HTML5 audio element with autoplay, pause and resume.
4. **File naming and output folder**
   - If I don’t set a custom prefix, the app uses the first Markdown heading as part of the filename.
   - Example output:
     - `azure_outputs/<cleaned_heading>_20251127_224839.mp3`
     - `azure_outputs/<cleaned_heading>_20251127_224839.mp4`
5. **YouTube description (optional)**
   - If I tick the checkbox, the app shows a text area that contains:
     - my processed text (one sentence per line)
     - a pre‑written German description + hashtags  
   - I can copy‑paste that straight into YouTube.

---

### Files

- `azure_tts_app.py`  
  Main app: Markdown → Azure TTS → MP3 / MP4 + YouTube description text.

- `azure_outputs/`  
  Output folder for audio and video (ignored by git).

- `.streamlit/secrets.toml`  
  Local secrets file, **not** committed. I create this myself.

- `.gitignore`  
  Keeps virtual envs, temp files, outputs and secrets out of the repo.

---

### Azure Free Tier (F0)

From Azure’s docs (I always check the latest pricing):

- Neural TTS in many regions gives me **about 500,000 characters per month for free**.  
- The UI shows:
  - characters for the current synthesis
  - an approximate percentage of that monthly 500,000‑character allowance.

As long as my total usage stays within the free quota, I don’t get charged.  
Real pricing and quotas depend on Azure’s current offering and my resource’s pricing tier.

---

### How I use this project

For me this project is both:

1. A **daily tool** to generate German listening and reading material.  
2. A small **lab** I can keep improving when I have new ideas.

My workflow:

- I treat this repo as my main project and use git commits to record changes and ideas instead of keeping lots of random files.  
- For bigger experiments (e.g. SRT generation, Anki export), I can create branches.  
- For daily learning, I stick to the stable flow: Markdown → Azure TTS → MP3/MP4 + description, then listen / shadow regularly.

---

## 中文說明

這個專案是我用來「把德文（或其他語言）文字快速變成高品質語音與影片」的小工具。  
核心是用 **Azure Speech Service (Text‑to‑Speech)** 搭配 **Streamlit** 做一個簡單的網頁介面。

### 我拿它來做什麼

- 我貼上 **Markdown 文本**，程式會自動去除標題、列表等標記，只保留適合朗讀的純文字。
- 它會把清理後的文字切成「一句一行」，方便我檢查或拿去做字幕。
- 它用 Azure Neural Voice 合成 **MP3 音檔**。
- 我可以選擇是否產生 **黑底 MP4 影片**，直接丟上 YouTube 很方便。
- 合成完成後，我可以選擇 **自動朗讀**，在瀏覽器裡播放（可以暫停 / 繼續）。
- 音檔與影片會自動存到 `azure_outputs/`，檔名包含：
  - Markdown 的第一個標題（清理後）
  - 時間戳（`YYYYMMDD_HHMMSS`）
- 我可以勾選一個選項，順便產生 **YouTube 說明欄文本**，把本次文本和固定的德文說明範本合在一起，一次複製貼上。

---

### 環境需求

- Python 3.9+（建議）
- 已建立 Azure Speech Service 資源（有 **Key** 跟 **Region**）

我用下面指令安裝套件：

```bash
pip install streamlit azure-cognitiveservices-speech
```

---

### Azure 金鑰設定（Streamlit secrets）

我用 `st.secrets` 來讀 Azure 金鑰。

1. 在專案根目錄建立資料夾：

   ```bash
   mkdir -p .streamlit
   ```

2. 新增 `.streamlit/secrets.toml`（這個檔案 **不會** 被 git 追蹤，`.gitignore` 已經排除了）：

   ```toml
   SPEECH_KEY = "你的 Azure Speech Key"
   SPEECH_REGION = "你的 Region，例如 eastasia"
   ```

啟動 Streamlit 時，程式會從 `st.secrets["SPEECH_KEY"]` 和 `st.secrets["SPEECH_REGION"]` 讀取設定。

> 如果要分享這個專案，我可以另外放一個 `.streamlit/secrets.toml.example` 給別人參考，但不要放真正的 key。

---

### 啟動 Azure TTS 介面

在專案根目錄執行：

```bash
streamlit run azure_tts_app.py
```

瀏覽器會自動開啟（或自己開 `http://localhost:8501`）。

介面大致流程：

1. **貼入 Markdown 文本**
   - 介面會自動：
     - 刪掉所有層級的標題（整行以 `#` 開頭的）
     - 去掉常見的 Markdown 標記和項目符號
     - 把內容合併成乾淨的純文字。
2. **檢查「每句一行」的預處理文本**
   - 程式會依 `.`、`?`、`!` 做簡單切句，一句顯示一行。
   - 下方會顯示這次送給 Azure 的字元數，以及大約佔每月 50 萬免費字元的比例。
3. **語音與輸出設定**
   - 我選一個 Azure Neural Voice（預設有幾個常用德文／英文 voice，也可以自己填名稱）。
   - 選輸出類型：
     - 只產生 MP3
     - 產生黑底 MP4（使用 `ffmpeg`）
   - 決定是否「合成完成後自動朗讀」：
     - 有勾選的話，用 HTML5 audio 自動播放，也可以暫停 / 繼續。
4. **檔名與輸出路徑**
   - 如果沒輸入自訂前綴，就用 Markdown 的第一個標題當作檔名的一部分。
   - 檔名大致像：
     - `azure_outputs/<清理後標題>_20251127_224839.mp3`
     - `azure_outputs/<清理後標題>_20251127_224839.mp4`
5. **YouTube 說明欄文本（選用）**
   - 勾選選項後，下方會多一個文字框，內容包含：
     - 本次預處理後的逐句文本
     - 預先寫好的德文說明欄 + Hashtags  
   - 我可以一次複製貼上到 YouTube。

---

### 檔案說明

- `azure_tts_app.py`  
  主介面：Markdown → Azure TTS → MP3 / MP4 + YouTube 說明欄文本。

- `azure_outputs/`  
  存放 Azure 朗讀與影片的資料夾（透過 `.gitignore` 排除，不會 push 到 GitHub）。

- `.streamlit/secrets.toml`  
  本機機密設定檔，**不會** 進入版控，需要自己建立。

- `.gitignore`  
  排除虛擬環境、暫存檔、輸出音檔／影片、secrets 等不該上傳的檔案。

---

### Azure 免費額度（F0 / Free Tier）

以目前 Azure 官方說明為主，大致是：

- 多數區域的 Neural TTS 每月有 **約 500,000 個字元的免費額度**。  
- 這個介面會顯示：
  - 這次朗讀的字元數
  - 約略佔 500,000 字元免費額度的百分比

只要每月總字元數沒有超過免費額度，就不會被收費。  
實際價格與額度還是要以 Azure 官方 Pricing 頁面與你的資源設定為準。

---

### 我怎麼用這個專案

對我來說，這個專案同時是：

1. 日常用的 **德文聽力／朗讀生產機**。  
2. 可以一直調整的小型 **個人實驗室（Lab）**。

我的使用方式：

- 我把這個倉庫當成主專案，用 git commit 記錄每次改動和想法，而不是留一堆零散檔案。  
- 想做比較大的新功能（例如自動 SRT、連到單字卡）時，就開一個新的 branch 慢慢玩。  
- 平常學習時，我就走最穩定那條流程：Markdown → Azure TTS → MP3/MP4 + 說明欄，當作聽力與跟讀素材。

---

### TODO / 之後可能會做的事

- 自動產生 SRT 字幕（依句子長度或時間分配）。
- 更完整的德文數字、日期、縮寫正規化。
- 把句子／單字匯出成單字卡格式（例如 Anki）。

我會把這個 lab 持續當成自己的德文工具箱，需要什麼功能就慢慢加上去。 

