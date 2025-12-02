# 工程日誌 (Engineering Log)

這個檔案用來紀錄本專案的功能調整、重構與實驗筆記，避免把 `README.md` 弄得太長、太複雜。  
`README.md` 只保留「怎麼用」與「環境設定」等必備資訊；任何細節優化都請寫在這裡。

---

## 2025-12-02

- 新增：`ENGINEERING_LOG.md`，作為之後所有優化與調整的紀錄位置。
- 調整：`clean_markdown` / `split_sentences`
  - 清洗 Markdown 時不再把所有行接成一行，而是盡量保留原始換行。
  - 分句改為「先依行拆，再在行內依標點切句」，確保原文本有換行的地方在結果中也一定會換行。
- 調整：YouTube 說明欄模板 `YOUTUBE_DESCRIPTION_TEMPLATES`
  - 確保所有模板都包含 Language Reactor 插件的學習小提醒。

