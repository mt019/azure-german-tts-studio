# German TTS Lab – Azure Speech + Streamlit

> 詳細的開發變更與優化紀錄，請參見 `ENGINEERING_LOG.md`。

## English

I built this small tool to turn German (or other language) text into high‑quality audio and simple black‑screen videos using **Azure Speech Service (Text‑to‑Speech)** and **Streamlit**.

### What this app does for me

- I paste **Markdown text**, and the app automatically removes most markup and list symbols.
- It keeps the **first heading** as the title sentence, and drops all later headings.
- It splits the cleaned text into **one sentence per line**, which makes it easy for me to check and reuse the text.
- It uses Azure Neural Voices to synthesize **German MP3 audio** (non‑German parts such as Chinese notes are meant to stay as on‑screen text, not audio).
- I can optionally generate a **black‑screen MP4 video** and choose how many seconds of silent black screen I want at the beginning.
- After synthesis, I can choose to **auto‑play the audio in the browser** (with pause / resume) or just play it manually.
- For every run, the app also writes a **subtitle‑friendly `.txt` file** (one sentence per line) to feed into YouTube.
- All outputs are stored in `azure_outputs/` with filenames that include:
  - the first Markdown heading (cleaned)
  - a timestamp (`YYYYMMDD_HHMMSS`)
- I can tick an option to **generate a YouTube description**, combining the current text with a reusable German description template (including a hint to use Language Reactor).

---

### Requirements

- Python 3.9+ (recommended)  
- An Azure Speech Service resource (with **Key** and **Region**)

I install the Python dependencies with:

```bash
pip install -r requirements.txt
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

---

### How I run the Azure TTS app

In the project root:

```bash
streamlit run azure_tts_app.py
```

The browser opens automatically (or I go to `http://localhost:8501`).

My workflow in the UI:

1. **Paste Markdown text（main area）**
   - The app:
     - keeps the first heading as a title sentence, drops later headings
     - removes common Markdown markup, list bullets and bold markers
     - joins everything into clean plain text.
2. **Check the “one sentence per line” view（main area）**
   - The app splits by `.`, `?`, `!` into sentences and shows them one per line.
3. **Configure everything in the sidebar**
   - I pick an Azure Neural Voice (German voices by default, or a custom voice name).
   - I choose output type:
     - only MP3
     - black‑screen MP4 (using `ffmpeg`)
   - I choose how many seconds of silent black screen I want at the **start of the MP4**.
   - I decide whether to **auto‑play after synthesis**.
   - I set an optional filename prefix (otherwise the first heading is used).
   - I choose a **YouTube description template purpose** (e.g. general listening, TestDaF listening / speaking / writing); this controls which reusable description text is used.
   - I can tick a checkbox to **generate a YouTube description** (text area in the main area). Above the checkbox, the app shows which template is currently selected, so the option always matches the template choice.
   - The sidebar also has a collapsible **YouTube description template** block, showing the currently selected reusable German description I can copy and tweak.
   - At the bottom of the sidebar there is a collapsible **usage info** block showing characters for this run and roughly what percentage of the free 500k‑character quota it consumes.
   - At the very top of the sidebar there is the **“Start synthesis”** button.
   - For long texts, I can choose between **“single pass”** and **“auto segmentation (recommended)”**:
     - auto segmentation splits the cleaned text into sentences and then groups a configurable number of sentences per segment (e.g. 3–12),
     - each segment is synthesized separately and then merged into one final MP3,
     - temporary segment files and ffmpeg concat lists are cleaned up automatically, so only the final MP3/MP4 and subtitle `.txt` remain in `azure_outputs/`.
4. **File naming and outputs**
   - If I don’t set a custom prefix, the app uses the first Markdown heading as part of the filename.
   - Example output:
     - `azure_outputs/<cleaned_heading>_20251127_224839.mp3`
     - `azure_outputs/<cleaned_heading>_20251127_224839.mp4`
     - `azure_outputs/<cleaned_heading>_20251127_224839.txt` (one sentence per line, for YouTube subtitles)

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

1. A **daily tool** to generate German listening, reading and speaking material (I use it a lot for shadowing / oral practice).  
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

- 我貼上 **Markdown 文本**，程式會自動清掉多數標記和項目符號。
- 它會保留「第一個標題」當作開頭句子，其餘標題會被丟掉。
- 它把清理後的文字切成「一句一行」，方便我檢查或拿去做字幕。
- 它用 Azure Neural Voice 合成 **德文 MP3 音檔**（中文註解之類只出現在畫面和文字檔，不進到音軌裡）。
- 我可以選擇是否產生 **黑底 MP4 影片**，還能設定影片開頭要先空幾秒黑畫面再開始講話。
- 合成完成後，我可以選擇 **自動朗讀**，在瀏覽器裡播放（可以暫停 / 繼續）。
- 每次合成時，程式也會輸出一個「**字幕用 .txt 檔**」（每句一行），方便拿去餵 YouTube 字幕。
- 音檔、影片與字幕文字檔會自動存到 `azure_outputs/`，檔名包含：
  - 清理過的第一個標題
  - 時間戳（`YYYYMMDD_HHMMSS`）
- 我可以勾選一個選項，順便產生 **YouTube 說明欄文本**，把本次文本和固定的德文說明範本（含 Language Reactor 推薦）合在一起，一次複製貼上。

---

### 環境需求

- Python 3.9+（建議）
- 已建立 Azure Speech Service 資源（有 **Key** 跟 **Region**）

我用下面指令安裝套件：

```bash
pip install -r requirements.txt
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

---

### 啟動 Azure TTS 介面

在專案根目錄執行：

```bash
streamlit run azure_tts_app.py
```

瀏覽器會自動開啟（或自己開 `http://localhost:8501`）。

介面大致流程：

1. **貼入 Markdown 文本（主畫面）**
   - 介面會自動：
     - 保留第一個標題作為開頭句子，其餘標題丟掉
     - 去掉常見的 Markdown 標記、項目符號與粗體標記
     - 把內容合併成乾淨的純文字。
2. **檢查「每句一行」的預處理文本（主畫面）**
   - 程式會依 `.`、`?`、`!` 做簡單切句，一句顯示一行。
3. **在側邊欄調整所有設定**
   - 我選一個 Azure Neural Voice（預設幾個德文／英文 voice，也可以自己填名稱）。
   - 選輸出類型：
     - 只產生 MP3
     - 產生黑底 MP4（使用 `ffmpeg`）
   - 設定「影片開頭空白幾秒」只影響 MP4，音訊本身不延遲。
   - 決定是否「合成完成後自動朗讀」。
   - 視需要輸入自訂檔名前綴（不填就用第一個標題）。
   - 選擇 **YouTube 說明欄用途 / 模板**（例如：一般聽力、德福聽力 / 口語 / 書寫），這會決定使用哪一段說明欄範本文字。
   - 勾選是否產生 YouTube 說明欄文本（會在主畫面顯示一個可複製的文字框），勾選上方會顯示「目前將使用哪一個模板」，確保選項與實際模板對得上。
   - 側邊欄中還有一個可收合的「YouTube 說明欄模板」區塊，會顯示目前選擇的德文說明欄範本，可以直接複製後再微調。
   - 側邊欄最底部有一個可以展開/收合的「文字用量」區塊，顯示這次送給 Azure 的字元數與約略占免費額度多少 %。
   - 側邊欄最上方就是「開始語音合成」按鈕。
   - 針對長文本，我可以選擇：
     - 「整篇一次合成」，或
     - 「自動分段（建議）」：會先把清理後的內容切成句子，再依「每段幾句」（例如 3–12 句）自動分成多段。
       - 每一段會分別丟給 Azure 合成，最後再自動用 ffmpeg 合併成一個完整的 MP3。
       - 中間產生的分段 mp3 檔與 ffmpeg 的清單檔會在合併成功後自動刪除，`azure_outputs/` 裡只會留下最終的 MP3 / MP4 / 字幕用 `.txt`。
4. **檔名與輸出路徑**
   - 如果沒輸入自訂前綴，就用 Markdown 的第一個標題當作檔名的一部分。
   - 檔名大致像：
     - `azure_outputs/<清理後標題>_20251127_224839.mp3`
     - `azure_outputs/<清理後標題>_20251127_224839.mp4`
     - `azure_outputs/<清理後標題>_20251127_224839.txt`（每句一行，給 YouTube 當字幕文字檔）

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

1. 日常用的 **德文聽力／朗讀／口說跟讀生產機**（我會搭配 shadowing 練口語）。  
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
